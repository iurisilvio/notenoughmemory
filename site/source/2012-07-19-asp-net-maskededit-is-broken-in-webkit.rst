ASP.NET MaskedEdit is broken in WebKit
######################################

:date: 2012-07-19
:tags: csharp, hack
:category: programming

Ajax Control Tookit is one of an important library in .NET world. It handles a lot of dynamic JavaScript things you do not want to do alone.

They have a component called MaskedEdit to handle a input formatted text like ``__/__/__``. Take a look at the `MaskedEdit example <http://www.asp.net/ajaxLibrary/AjaxControlToolkitSampleSite/MaskedEdit/MaskedEdit.aspx>`_. Oh, if you use Chrome or Safari, it does not work like you expect with delete, backspace and other "special" keys. Cool, han?

This bug is from 2008, documented in `issue 26978 <http://ajaxcontroltoolkit.codeplex.com/workitem/26978>`_, `issue 17166 <http://ajaxcontroltoolkit.codeplex.com/workitem/17166>`_ and `chromium issue 3341 too <http://code.google.com/p/chromium/issues/detail?id=3341>`_. These links have easy solutions: just take the code, change a couple of lines and recompile everything, but it was never merged or released.

I do not want to fork the code to change two lines, but I can just hack around JavaScript and we are fine. If you opened the MaskedEdit example in Chrome, run the code below in JavaScript console and try again. I took some pieces of code around the internet and wrote my own to work with normal and minified versions of current version of the lib.

.. code:: javascript
    
    (function() {
      if (Sys.Browser.agent == Sys.Browser.Safari) { // don't worry, to this lib Chrome is Safari
        function funcbody(f) {
          var s = f.toString();
          return s.substring(s.indexOf('{'));
        }
        try { p = Sys.Extended.UI.MaskedEditBehavior.prototype; } catch (e) { p = null; }
        if (p != null) {
          p._ExecuteNav = new Function("g", "h",
            'var c=-1,e=" ",a="",b=false,d=true,p="keypress",s="keydown",evt=g,scanCode=h;' +
            funcbody(p._ExecuteNav)
              .replace(/(g\.type==p\)if\(h==8\))/, "g.type==s||$1")
              .replace(/(== Sys\.Browser\.InternetExplorer \|\| evt\.type == \"keypress\")/,
                       "$1 || evt.type == \"keydown\""));
          }
        }
    })();


The problem happens because the ``MaskedEditBehavior`` handles only ``keypress`` event (or bypass IE browsers). My hack just changes it to handle ``keydown`` too, because `W3C says <http://www.w3.org/TR/2010/WD-DOM-Level-3-Events-20100907/#event-type-keypress>`_ "dispatch this event when a key is pressed down, if and only if that key normally produces a character value".

This hack solved the issue to me and is running in production now, but it is a big reason to avoid Ajax Control Toolkit if you can. Maybe they will not support you.
