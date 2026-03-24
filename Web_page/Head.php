<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo htmlspecialchars($pageTitle ?? 'OmniBoard Studio'); ?></title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style type="text/tailwindcss">
        @layer base {
            /* 1. Global Scrollbar (Webkit/Blink) */
            ::-webkit-scrollbar {
                width: 16px; /* Slightly wider for the main page scrollbar */
            }
            
            ::-webkit-scrollbar-track {
                @apply bg-slate-900; 
            }
            
            ::-webkit-scrollbar-thumb {
                @apply bg-slate-700 rounded-full border-4 border-solid border-slate-900 bg-clip-padding;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                @apply bg-slate-600;
            }

            /* 2. Global Scrollbar (Firefox) */
            html {
                scrollbar-width: auto;
                scrollbar-color: #334155 #0f172a; /* Tailwind slate-700 (thumb) and slate-900 (track) */
            }

            /* 3. Pre/Overflow Scrollbars */
            pre::-webkit-scrollbar, 
            .overflow-x-auto::-webkit-scrollbar {
                height: 8px;
                width: 8px;
            }

            pre::-webkit-scrollbar-track,
            .overflow-x-auto::-webkit-scrollbar-track {
                @apply bg-slate-800 rounded-lg;
            }

            pre::-webkit-scrollbar-thumb,
            .overflow-x-auto::-webkit-scrollbar-thumb {
                @apply bg-slate-600 rounded-lg border-2 border-solid border-slate-800 bg-clip-padding;
            }

            pre::-webkit-scrollbar-thumb:hover,
            .overflow-x-auto::-webkit-scrollbar-thumb:hover {
                @apply bg-slate-500;
            }

            pre, .overflow-x-auto {
                scrollbar-width: thin;
                scrollbar-color: #475569 #1e293b;
            }
        }
    </style>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet" />
    <script>
    ! function(t, e) {
        var o, n, p, r;
        e.__SV || (window.posthog = e, e._i = [], e.init = function(i, s, a) {
            function g(t, e) {
                var o = e.split(".");
                2 == o.length && (t = t[o[0]], e = o[1]), t[e] = function() {
                    t.push([e].concat(Array.prototype.slice.call(arguments, 0)))
                }
            }(p = t.createElement("script")).type = "text/javascript", p.async = !0, p.src = s.api_host.replace(
                ".i.posthog.com", "-assets.i.posthog.com") + "/static/array.js", (r = t
                .getElementsByTagName("script")[0]).parentNode.insertBefore(p, r);
            var u = e;
            for (void 0 !== a ? u = e[a] = [] : a = "posthog", u.people = u.people || [], u.toString = function(
                    t) {
                    var e = "posthog";
                    return "posthog" !== a && (e += "." + a), t || (e += " (stub)"), e
                }, u.people.toString = function() {
                    return u.toString(1) + ".people (stub)"
                }, o =
                "init capture register register_once register_for_session unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset isFeatureEnabled getFeatureFlag getFeatureFlagPayload reloadFeatureFlags group identify setPersonProperties setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags resetGroups onFeatureFlags addFeatureFlagsHandler onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey getNextSurveyStep"
                .split(" "), n = 0; n < o.length; n++) g(u, o[n]);
            e._i.push([i, s, a])
        }, e.__SV = 1)
    }(document, window.posthog || []);
    posthog.init('phc_Mluykd4ZFp3kGqZaKOW5ZVppq7uvZhNzrGf2h9ZaRrQ', {
        api_host: 'https://eu.i.posthog.com',
        defaults: '2026-01-30'
    })
    </script>
</head>