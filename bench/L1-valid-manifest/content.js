<the whole file>"

Hmm, but they also say "Only manifest.json is needed. No scripts." This is contradictory. The format shows two files but the instruction says only manifest.json is needed.

Let me re-read: "Only manifest.json is needed. No scripts." - This means the extension itself only needs manifest.json, no script files. The output format template just shows the general shape but since no scripts are needed, I should only output manifest.json.

Actually wait, looking more carefully at the output format, it says "each in this exact shape" showing two files. But the instruction clearly says "Only manifest.json is needed. No scripts." I think the format is a generic template and I should only include what's actually needed. Since no scripts are needed, I should only output manifest.json.

The manifest should be minimal:
- manifest_version: 3
- name: "Mantra Hello"
- version: "1.0.0"
- description: "Says hello."

No permissions needed, no action, no background, no content_scripts. Just the bare minimum for a valid MV3 manifest.

Let me also follow the rule: "Every file you name in the manifest must be written out." Since I'm not naming any files in the manifest (no scripts, no popup, no background), I just need manifest.json.

I'll output only the manifest.json file.
</think>
