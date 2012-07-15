Some ways to remove a Facebook post
###################################

:date: 2012-05-06
:tags: funblocker, hack
:category: programming

During my adventures developing `FunBlocker <https://chrome.google.com/webstore/detail/cgdkiknkffmdbonojkcofooaampcefom>`_, I needed to hide some Facebook posts.

Here is some of my code history in GitHub, analysing my different solutions to this problem.

Just hide it
************

My first solution was just hide the post with CSS ``display:none``, when I still ran it with `JavaScript Injector <https://chrome.google.com/webstore/detail/abdogfafejmdomllalkdegagoehgbdbk>`_ and jQuery. It was an easy task, `my first commit had only 12 lines of code <https://github.com/iurisilvio/FunBlocker/blob/2853f5f6473153d1ebf6b9154bf98724429a2e01/main.js#L7>`_. You can check the whole code there.

Remove DOM element
******************

When I turned FunBlocker in a Chrome Extension, I decided not to depend on `jQuery <http://www.jquery.com>`_, because it will run in background of Facebook and should not slow down the timeline performance. Or maybe I decided that because I never had programmed these basic things without jQuery.

So, I find a link in a post I want to remove from the DOM.

.. code:: html

    <!-- Facebook HTML posts tree looks like this -->
    <ul>
        <li>
            <div class="storyContent">
                [your friend sharing some shit here]
                <a>Page I do not want here</a>
            </div>
        </li>
    </ul>

I search for links and get the parent element with class containing ``storyContent``. After that, I call ``remove_story``:

.. code:: javascript

    function remove_story(story) {
        var node = story;
        var parent = node.parentNode;
        while (parent.tagName != 'UL') {
            var tmp = parent;
            parent = parent.parentNode;
            node = tmp;
        }
        parent.removeChild(node);
    }

It was more code than my first version, but I learnt a lot without the jQuery dependency. At this moment, I had `62 lines of code <https://github.com/iurisilvio/FunBlocker/blob/b57200734740e31c7505d9ab737041945943b7dd/fb.js#L14>`_ on GitHub.

Click Hide Story
****************

Facebook has an option in menu to remove the content from your timeline. How can I use it? Without jQuery it is not a streight forward task. The code below do almost the same thing than ``$(element).click()``.

.. code:: javascript

    var event_ = document.createEvent("MouseEvents");
    event_.initEvent("click", true, true); // event type, bubbling, cancelable
    if (element) { // element is the link I want to click
        element.dispatchEvent(event_);
    }

Yes, sometimes it works. Other times Facebook just do not have the link I want because it is dinamically loaded. To solve this problem, I want to trigger the loading and after that click the button I need.

I preferred another approach.

Mimic Facebook
**************

I know the click discussed above trigger some action to Facebook servers. The ``Hide Story`` button triggers a HTTP call to ``https://www.facebook.com/ajax/feed/filter_action/uninteresting/?__a=1`` with some trick parameters. If I do the same thing, everything works.

After some research and reverse engineering in Facebook messages, JavaScript and HTML, I understanded a bit about what are these parameters and how to do this one call to Facebook.

To be honest, I do not know how exactly it works, but it is there and makes my timeline better everyday. If you need something like that, take a look at `try_default_hide function <https://github.com/iurisilvio/FunBlocker/blob/5a0070ce5a6df8d49e41a58aa66801dcf3e90afe/fb.js#L119>`_. I spent some days to solve this problem and did not found documentation about it.