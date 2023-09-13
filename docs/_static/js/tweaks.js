// Show subsections in the navigation bar of the File Format document.
//
// It's helpful to understand how the navigation bar styling is supposed to 
// work, to see why it doesn't normally show subsections.  Here are the 
// steps:
//
// - Sphinx RTD theme only includes in the navigation bar links that have a 
//   parent of class `.current`.  The HTML for any other links is present, 
//   but hidden.
//
// - Sphinx add the `.current` class to links that point to the current page.  
//   All ancestors of a "current" link are also given the `.current` class.  
//   The idea is that themes might want to apply a unique style to the links 
//   leading up to the current page.  Importantly, links that point within 
//   the current page, not to the page as a whole (i.e. sections and 
//   subsections), are not considered current.
//
// - Ultimately, this all means that only top-level sections are included in 
//   the navigation bar.
//
// I initially tried taking an approach where I manually added the `.current` 
// class to the necessary elements to get the subsection links to appear.  
// The upside was that I didn't have to hard-code the padding, but the 
// downside was the font weight and background color were also (undesireably) 
// affected.  I decided that it was easier to just apply the specific styles 
// I wanted.
//
// It might be possible to avoid the hard-coding by querying the style sheets 
// somehow, e.g. `document.styleSheets`.  But this seemed like to much effort 
// for something that could break in many other ways anyways.

document.addEventListener("DOMContentLoaded", function(){
  subsection_docs = [
    'file_format.html',
    'basic_usage_python.html',
    'basic_usage_r.html',
  ]
  is_subsection_doc = subsection_docs.some(
    (p) => window.location.pathname.endsWith(p)
  )
  if(! is_subsection_doc) {
    return
  }

  ul = document.querySelectorAll('.toctree-l2 > ul');
  for(var i = 0; i < ul.length; i++) {
    ul[i].style.display = 'block';

    a = ul[i].querySelectorAll('.toctree-l3 > a');
    for(var j = 0; j < a.length; j++) {
      // The padding come from the following selector (note the `.current`):
      // `.wy-menu-vertical li.toctree-l2.current li.toctree-l3>a`
      a[j].style.padding = '.4045em 1.618em .4045em 4.045em'
    }
  }
});

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

  ul = document.querySelector('.toctree-l2.current > ul');
  ul.style.display = 'none';
});


