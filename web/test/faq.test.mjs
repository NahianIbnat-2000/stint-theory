// FAQ content: unique ids, known groups, links to real pages, plain-language rules.
import { test } from "node:test";
import assert from "node:assert/strict";
import { FAQ, GROUPS } from "../src/content/faq.js";
import { filterFaq } from "../src/lib/faq.js";
import { ROUTES } from "../src/routes.js";

test("every FAQ item has a unique id, a known group and an answer", () => {
  const ids = FAQ.map((f) => f.id);
  assert.equal(new Set(ids).size, ids.length);
  const groups = new Set(GROUPS.map((g) => g.id));
  for (const f of FAQ) {
    assert.ok(groups.has(f.group), f.id);
    assert.ok(f.q.endsWith("?"), f.id);
    assert.ok(f.a.length > 0, f.id);
  }
  for (const g of GROUPS) assert.ok(FAQ.some((f) => f.group === g.id), g.id);
});

test("every FAQ link points to a page that exists", () => {
  const paths = new Set(ROUTES.map((r) => r.path));
  for (const f of FAQ) for (const l of f.links || []) assert.ok(paths.has(l.to), `${f.id} -> ${l.to}`);
});

test("FAQ copy avoids em dashes", () => {
  for (const f of FAQ) assert.ok(![f.q, ...f.a, f.fact || ""].join(" ").includes("—"), f.id);
});

test("FAQ filter matches by group and by words in any order", () => {
  assert.equal(filterFaq(FAQ, "all", "").length, FAQ.length);
  assert.ok(filterFaq(FAQ, "f1", "").every((f) => f.group === "f1"));
  assert.ok(filterFaq(FAQ, "all", "SAFETY car").some((f) => f.id === "safety-car"));
  assert.ok(filterFaq(FAQ, "all", "car safety").some((f) => f.id === "safety-car"));
  assert.equal(filterFaq(FAQ, "all", "zzzz").length, 0);
});
