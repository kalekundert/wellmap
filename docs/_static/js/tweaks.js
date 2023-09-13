// Don't show subsections in the Python API docs.
//
// This is really a hacky work-around to an missing feature in autodoc.  
// Directives like `.. function::` have the `:no-contents-entry:` option to 
// prevent them from appearing in the TOC, but `.. autofunction::` doesn't 
// expose this.  So the only alternative I can think of is to hide these links 
// after the fact.

document.addEventListener("DOMContentLoaded", function(){
  api_pattern = /api\/wellmap.*html$/

  if (! window.location.pathname.match(api_pattern)) {
    return
  }

  ul = document.querySelector('li.toctree-l2.current > ul');
  ul.style.display = 'none';

  // This prevents the theme from adding an expand/collapse button.  Note that 
  // this script happens beofre the theme does; not sure why.
  ul.classList.add("simple");
});


