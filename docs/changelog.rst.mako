********
Versions
********

Wellmap adheres to `semantic versioning <https://semver.org/>`_.  Briefly, this 
means that minor version upgrades (e.g. 1.1 to 1.2) should never break any 
existing code, while major version upgrades (e.g. 1.1 to 2.0) might.

% for version in data["versions"]:
<%
title = "%s (%s)" % (version["tag"], version["date"]) if version["tag"] else opts["unreleased_version_label"]
nb_sections = len(version["sections"])
%>${title}
${"=" * len(title)}
% for section in version["sections"]:
% if not (section["label"] == "Other" and nb_sections == 1):

${section["label"]}
${"-" * len(section["label"])}
% endif
% for commit in section["commits"]:
<%
subject = "%s [%s]" % (commit["subject"], ", ".join(commit["authors"]))
entry = indent('\n'.join(textwrap.wrap(subject)), first="- ").strip()
%>${entry}

% if commit["body"]:
${indent(commit["body"])}

% endif
% endfor
% endfor

% endfor
