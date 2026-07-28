/*
 * DocC render JSON -> Markdown converter for Swift Package Index docs.
 *
 * Runs INSIDE a browser page on https://swiftpackageindex.com so that the
 * same-origin `fetch` carries the Cloudflare clearance cookie (a plain HTTP
 * client — curl, requests, WebFetch — is blocked by the "Just a moment..."
 * managed challenge).
 *
 * Exposes `window.__spiDocc.convert(url)` -> Promise<{ url, title, markdown }>.
 *
 * `url` is a human documentation URL, e.g.
 *   https://swiftpackageindex.com/groue/GRDB.swift/master/documentation/grdb
 * The converter derives the data endpoint
 *   /{owner}/{repo-lowercased}/{ref}/data/documentation/grdb.json
 * and rewrites every cross-reference back into a followable human URL, so the
 * emitted "Topics" / "See Also" links can be fed straight back into convert().
 */
(function () {
  "use strict";

  // ---- URL helpers -------------------------------------------------------
  function parseDocURL(input) {
    const u = new URL(input, "https://swiftpackageindex.com");
    const segs = u.pathname.split("/").filter(Boolean); // owner, repo, ref, "documentation", ...
    const docIdx = segs.indexOf("documentation");
    if (docIdx < 3) throw new Error("Not an SPI documentation URL: " + u.pathname);
    const owner = segs[0], repo = segs[1], ref = segs[2];
    const docPath = "/" + segs.slice(docIdx).join("/"); // /documentation/grdb/...
    const base = `${u.origin}/${owner}/${repo.toLowerCase()}/${ref}`;
    return { origin: u.origin, owner, repo, ref, base, docPath };
  }
  function dataURL(ctx) {
    return `${ctx.base}/data${ctx.docPath.replace(/\/$/, "")}.json`;
  }
  // A DocC reference -> followable human SPI URL (or external link untouched).
  function humanURL(ctx, ref) {
    if (!ref) return null;
    const p = ref.url;
    if (p && p.startsWith("/documentation")) {
      return `${ctx.origin}/${ctx.owner}/${ctx.repo}/${ctx.ref}${p}`;
    }
    return p || null;
  }
  function assetURL(ctx, ref) {
    if (!ref) return null;
    if (ref.variants && ref.variants.length) {
      const pick = ref.variants.find(v => (v.traits || []).includes("light")) || ref.variants[0];
      const p = pick.url;
      return p && p.startsWith("/") ? ctx.origin + p : p;
    }
    return ref.url || null;
  }

  // ---- inline content ----------------------------------------------------
  function inline(ctx, nodes) {
    if (!nodes) return "";
    return nodes.map(n => inlineOne(ctx, n)).join("");
  }
  function inlineOne(ctx, n) {
    switch (n.type) {
      case "text": return n.text;
      case "codeVoice": return "`" + n.code + "`";
      case "emphasis": return "*" + inline(ctx, n.inlineContent) + "*";
      case "strong": return "**" + inline(ctx, n.inlineContent) + "**";
      case "strikethrough": return "~~" + inline(ctx, n.inlineContent) + "~~";
      case "newTerm":
      case "inlineHead": return "**" + inline(ctx, n.inlineContent) + "**";
      case "image": {
        const ref = ctx.refs[n.identifier];
        const url = assetURL(ctx, ref);
        const alt = (ref && ref.alt) || "";
        return url ? `![${alt}](${url})` : "";
      }
      case "reference": {
        const ref = ctx.refs[n.identifier];
        if (!ref) return n.identifier || "";
        const text = ref.title
          || (ref.fragments ? ref.fragments.map(f => f.text).join("") : n.identifier);
        const url = humanURL(ctx, ref);
        return url ? `[${text}](${url})` : "`" + text + "`";
      }
      case "link":
        return `[${n.title || n.text || n.destination}](${n.destination})`;
      default:
        if (n.inlineContent) return inline(ctx, n.inlineContent);
        if (n.text) return n.text;
        return "";
    }
  }

  // ---- block content -----------------------------------------------------
  function blocks(ctx, nodes, depth) {
    depth = depth || 0;
    if (!nodes) return [];
    return nodes.map(n => blockOne(ctx, n, depth)).filter(s => s !== "");
  }
  function blockOne(ctx, n, depth) {
    switch (n.type) {
      case "heading":
        return n.text ? "#".repeat(Math.min(6, n.level || 2)) + " " + n.text : "";
      case "paragraph":
        return inline(ctx, n.inlineContent).trim();
      case "codeListing":
        return "```" + (n.syntax || "") + "\n" + (n.code || []).join("\n") + "\n```";
      case "unorderedList":
        return n.items.map(it => bulletItem(ctx, it, depth, "-")).join("\n");
      case "orderedList":
        return n.items.map((it, i) => bulletItem(ctx, it, depth, ((n.start || 1) + i) + ".")).join("\n");
      case "aside": {
        const label = n.name || n.style || "Note";
        const body = blocks(ctx, n.content, depth).join("\n\n");
        return body.split("\n").map(l => "> " + l).join("\n").replace(/^> /, `> **${label}:** `);
      }
      case "termList":
        return (n.items || []).map(it =>
          "- **" + inline(ctx, it.term.inlineContent) + "** — " +
          blocks(ctx, it.definition.content, depth).join(" ")
        ).join("\n");
      case "table":
        return table(ctx, n);
      case "links":
        return (n.items || []).map(id => {
          const ref = ctx.refs[id];
          return ref ? "- " + linkLine(ctx, ref) : "";
        }).filter(Boolean).join("\n");
      default:
        if (n.content) return blocks(ctx, n.content, depth).join("\n\n");
        if (n.inlineContent) return inline(ctx, n.inlineContent);
        return "";
    }
  }
  function bulletItem(ctx, item, depth, marker) {
    const inner = blocks(ctx, item.content, depth + 1);
    const first = (inner[0] || "").trim();
    const rest = inner.slice(1);
    const pad = "  ".repeat(depth);
    let s = pad + marker + " " + first;
    for (const r of rest) s += "\n" + r.split("\n").map(l => pad + "  " + l).join("\n");
    return s;
  }
  function table(ctx, n) {
    const rows = (n.rows || []).map(r =>
      r.map(cell => inline(ctx, (cell[0] && cell[0].inlineContent) || []).replace(/\|/g, "\\|")));
    if (!rows.length) return "";
    const header = rows[0];
    const line = r => "| " + r.join(" | ") + " |";
    return [line(header), line(header.map(() => "---")), ...rows.slice(1).map(line)].join("\n");
  }
  function linkLine(ctx, ref) {
    const title = ref.title
      || (ref.fragments ? ref.fragments.map(f => f.text).join("") : ref.identifier);
    const url = humanURL(ctx, ref);
    const abstract = ref.abstract ? " — " + inline(ctx, ref.abstract) : "";
    return url ? `[${title}](${url})${abstract}` : `${title}${abstract}`;
  }

  // ---- symbol sections ---------------------------------------------------
  function declarations(ctx, sec) {
    return (sec.declarations || [])
      .map(d => "```swift\n" + (d.tokens || []).map(t => t.text).join("") + "\n```")
      .join("\n\n");
  }
  function parameters(ctx, sec) {
    const items = (sec.parameters || [])
      .map(p => "- **`" + p.name + "`** — " + blocks(ctx, p.content, 0).join(" "));
    return items.length ? "**Parameters**\n\n" + items.join("\n") : "";
  }

  // ---- top-level render --------------------------------------------------
  function render(ctx, doc) {
    const md = [];
    const meta = doc.metadata || {};
    md.push("# " + (meta.title || "Documentation"));

    const role = meta.roleHeading || meta.symbolKind || null;
    const module = meta.modules && meta.modules[0] && meta.modules[0].name;
    const tagline = [role, module && `Module: ${module}`].filter(Boolean).join(" · ");
    if (tagline) md.push("*" + tagline + "*");

    if (doc.abstract) md.push(inline(ctx, doc.abstract).trim());

    for (const sec of doc.primaryContentSections || []) {
      if (sec.kind === "declarations") {
        const d = declarations(ctx, sec);
        if (d) md.push(d);
      } else if (sec.kind === "content") {
        md.push(...blocks(ctx, sec.content, 0));
      } else if (sec.kind === "parameters") {
        const p = parameters(ctx, sec);
        if (p) md.push(p);
      } else if (sec.kind === "possibleValues") {
        const items = (sec.values || []).map(v =>
          "- `" + v.name + "`" + (v.content ? " — " + blocks(ctx, v.content, 0).join(" ") : ""));
        if (items.length) md.push("**Possible values**\n\n" + items.join("\n"));
      }
    }

    for (const [key, title] of [["topicSections", "## Topics"], ["seeAlsoSections", "## See Also"]]) {
      const secs = doc[key] || [];
      if (!secs.length) continue;
      md.push(title);
      for (const t of secs) {
        if (t.title) md.push("### " + t.title);
        md.push((t.identifiers || []).map(id => {
          const ref = ctx.refs[id];
          return ref ? "- " + linkLine(ctx, ref) : "- " + id;
        }).join("\n"));
      }
    }

    return md.filter(s => (s || "").trim() !== "").join("\n\n") + "\n";
  }

  // ---- public entry ------------------------------------------------------
  async function convert(input) {
    const ctx = parseDocURL(input);
    const url = dataURL(ctx);
    const res = await fetch(url, { headers: { accept: "application/json" } });
    if (!res.ok) throw new Error("fetch " + url + " -> HTTP " + res.status);
    const doc = await res.json();
    ctx.refs = doc.references || {};
    return { url, title: (doc.metadata || {}).title, markdown: render(ctx, doc) };
  }

  window.__spiDocc = { convert, parseDocURL, dataURL };
})();
