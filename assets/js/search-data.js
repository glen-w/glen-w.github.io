// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "about",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-projects",
          title: "projects",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/projects/";
          },
        },{id: "nav-creative",
          title: "creative",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/creative/";
          },
        },{id: "nav-library",
          title: "library",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/library/";
          },
        },{id: "nav-blog",
          title: "blog",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/blog/";
          },
        },{id: "dropdown-bookshelf",
              title: "bookshelf",
              description: "",
              section: "Dropdown",
              handler: () => {
                window.location.href = "/books/";
              },
            },{id: "dropdown-catalogue-of-failures",
              title: "catalogue of failures",
              description: "",
              section: "Dropdown",
              handler: () => {
                window.location.href = "/failures/";
              },
            },{id: "dropdown-code",
              title: "code",
              description: "",
              section: "Dropdown",
              handler: () => {
                window.location.href = "/code/";
              },
            },{id: "dropdown-jingle",
              title: "jingle",
              description: "",
              section: "Dropdown",
              handler: () => {
                window.location.href = "/jingle/";
              },
            },{id: "dropdown-map",
              title: "map",
              description: "",
              section: "Dropdown",
              handler: () => {
                window.location.href = "/map.html";
              },
            },{id: "dropdown-pieces-of-paper",
              title: "pieces of paper",
              description: "",
              section: "Dropdown",
              handler: () => {
                window.location.href = "https://glen.trilium.cc/share/pieces_of_paper";
              },
            },{id: "dropdown-sitemap",
              title: "sitemap",
              description: "",
              section: "Dropdown",
              handler: () => {
                window.location.href = "/sitemap/";
              },
            },{id: "nav-cv",
          title: "cv",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/cv/";
          },
        },{id: "post-",
        
          title: "",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/2018-12-08-This-is-the-last-academic-conference-that-I-will-ever-go-to/";
          
        },
      },{id: "post-",
        
          title: "",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/2017-04-25-This-Study-is-Subject-to-Certain-Limitations_-Overly-Honest-Academic-Caveats/";
          
        },
      },{id: "post-",
        
          title: "",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/2016-07-12-Campus-Chaos-as-Pokemon-Go-Goes-Viral/";
          
        },
      },{id: "post-",
        
          title: "",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/2015-07-22-7-Academic-Struggles-Predicted-by-Late-19th-and-Early-20th-Century-Autobiographies/";
          
        },
      },{id: "post-",
        
          title: "",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/2015-07-17-The-Blooper-Reel/";
          
        },
      },{id: "post-",
        
          title: "",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/2015-04-04-Academic-Easter-Eggs/";
          
        },
      },{id: "post-",
        
          title: "",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/2015-02-14-An-Academic-Guide-to-Love-&amp;-Romance-Happy-Valentine&-039;s-Day!/";
          
        },
      },{id: "post-",
        
          title: "",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/2015-01-10-10-Brilliantly-Banal-Books-to-Bore-Your-Bookshelf/";
          
        },
      },{id: "post-",
        
          title: "",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/2014-10-31-Trick-or-Treat/";
          
        },
      },{id: "post-",
        
          title: "",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/2014-09-13-Every-Type-of-Email-College-Faculty-Send-to-Anyone/";
          
        },
      },{id: "post-",
        
          title: "",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2026/2014-08-01-Top-8-AlternateScienceMetrics/";
          
        },
      },{id: "post-a-quick-website-update",
        
          title: "a quick website update",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2025/a-quick-website-update/";
          
        },
      },{id: "post-the-fourth-annual-academics-with-cats-awards-2017-winners",
        
          title: "The Fourth Annual Academics with Cats Awards 2017 - Winners!",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2017/The-Fourth-Annual-Academics-with-Cats-Awards-2017-Winners!/";
          
        },
      },{id: "post-13-great-gifts-for-academics",
        
          title: "13 Great Gifts for Academics",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2017/13-Great-Gifts-for-Academics/";
          
        },
      },{id: "post-the-fourth-annual-academics-with-cats-awards",
        
          title: "The Fourth Annual Academics with Cats Awards",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2017/The-Fourth-Annual-Academics-with-Cats-Awards/";
          
        },
      },{id: "post-academia-obscura-book-out-now",
        
          title: "Academia Obscura book - out now!",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2017/Academia-Obscura-book-out-now!/";
          
        },
      },{id: "post-404-buffalo-not-found",
        
          title: "404 - Buffalo not found",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2017/404-Buffalo-not-found/";
          
        },
      },{id: "post-52-books-you-might-not-like",
        
          title: "52 Books You Might Not Like",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2017/52-Books-You-Might-Not-Like/";
          
        },
      },{id: "post-oops",
        
          title: "Oops!",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2017/Oops!/";
          
        },
      },{id: "post-the-story-behind-a-moving-academic-acknowledgement",
        
          title: "The Story Behind a Moving Academic Acknowledgement",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2017/The-Story-Behind-a-Moving-Academic-Acknowledgement/";
          
        },
      },{id: "post-you-must-be-very-intelligent-the-phd-delusion",
        
          title: "You Must Be Very Intelligent - The PhD Delusion",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2017/You-Must-Be-Very-Intelligent-The-PhD-Delusion/";
          
        },
      },{id: "post-doodling-for-academics",
        
          title: "Doodling for Academics",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2017/Doodling-for-Academics/";
          
        },
      },{id: "post-these-awesome-science-march-signs-prove-scientists-have-a-sense-of-humour",
        
          title: "These Awesome Science March Signs Prove Scientists have a Sense of Humour",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2017/These-Awesome-Science-March-Signs-Prove-Scientists-have-a-Sense-of-Humour/";
          
        },
      },{id: "post-how-broken-is-academia-and-how-can-we-fix-it",
        
          title: "How ‘broken’ is academia, and how can we fix it?",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2017/How-broken-is-academia,-and-how-can-we-fix-it/";
          
        },
      },{id: "post-6-examples-of-whimsical-acronyms-in-scientific-papers-sexwasp",
        
          title: "6 Examples of Whimsical Acronyms in Scientific Papers (SEXWASP)",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2017/6-Examples-of-Whimsical-Acronyms-in-Scientific-Papers-(SEXWASP)/";
          
        },
      },{id: "post-the-third-annual-academics-with-cats-awards-2016-winners",
        
          title: "The Third Annual Academics with Cats Awards 2016 - Winners!",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2016/The-Third-Annual-Academics-with-Cats-Awards-2016-Winners!/";
          
        },
      },{id: "post-academics-with-cats-awards-2016-the-shortlist",
        
          title: "Academics with Cats Awards 2016 - The Shortlist",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2016/Academics-with-Cats-Awards-2016-The-Shortlist/";
          
        },
      },{id: "post-the-third-annual-academics-with-cats-awards",
        
          title: "The Third Annual Academics with Cats Awards!",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2016/The-Third-Annual-Academics-with-Cats-Awards!/";
          
        },
      },{id: "post-on-commonplace-books",
        
          title: "On Commonplace Books",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2016/On-Commonplace-Books/";
          
        },
      },{id: "post-6-phrases-that-should-be-banned",
        
          title: "6 Phrases that Should be Banned",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2016/6-Phrases-that-Should-be-Banned/";
          
        },
      },{id: "post-sample-cover-letter-for-journal-manuscript-resubmissions",
        
          title: "Sample Cover Letter for Journal Manuscript Resubmissions",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2016/Sample-Cover-Letter-for-Journal-Manuscript-Resubmissions/";
          
        },
      },{id: "post-shit-i-learned-during-my-phd",
        
          title: "Shit I learned during my PhD",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2016/Shit-I-learned-during-my-PhD/";
          
        },
      },{id: "post-how-to-science",
        
          title: "How to: Science",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2016/How-to_-Science/";
          
        },
      },{id: "post-25-phd-feels-all-doctoral-students-have",
        
          title: "25 PhD Feels All Doctoral Students Have",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2016/25-PhD-Feels-All-Doctoral-Students-Have/";
          
        },
      },{id: "post-historic-un-talks-could-save-the-high-seas",
        
          title: "Historic UN talks could save the high seas",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2016/Historic-UN-talks-could-save-the-high-seas/";
          
        },
      },{id: "post-academics-with-cats-awards-2015-winners",
        
          title: "Academics with Cats Awards 2015 - WINNERS!",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/Academics-with-Cats-Awards-2015-WINNERS!/";
          
        },
      },{id: "post-5-out-of-this-world-star-wars-papers",
        
          title: "5 Out of this World Star Wars Papers",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/5-Out-of-this-World-Star-Wars-Papers/";
          
        },
      },{id: "post-11-terrible-video-game-screenshots-that-perfectly-capture-academic-life",
        
          title: "11 Terrible Video Game Screenshots that Perfectly Capture Academic Life",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/11-Terrible-Video-Game-Screenshots-that-Perfectly-Capture-Academic-Life/";
          
        },
      },{id: "post-the-second-annual-academics-with-cats-awards",
        
          title: "The Second Annual Academics with Cats Awards!",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/The-Second-Annual-Academics-with-Cats-Awards!/";
          
        },
      },{id: "post-still-not-significant",
        
          title: "Still. Not. Significant.",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/Still.-Not.-Significant/";
          
        },
      },{id: "post-a-new-academic-year-begins-bring-on-the-ig-nobels",
        
          title: "A New Academic Year Begins... Bring on the Ig Nobels!",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/A-New-Academic-Year-Begins/.-Bring-on-the-Ig-Nobels!/";
          
        },
      },{id: "post-12-things-i-learned-about-academia-from-google-suggestions",
        
          title: "12 Things I Learned About Academia from Google Suggestions",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/12-Things-I-Learned-About-Academia-from-Google-Suggestions/";
          
        },
      },{id: "post-10-quite-useful-tools-for-academics",
        
          title: "10 Quite Useful Tools for Academics",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/10-Quite-Useful-Tools-for-Academics/";
          
        },
      },{id: "post-11-essential-hashtags-for-academics",
        
          title: "11 Essential Hashtags for Academics",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/11-Essential-Hashtags-for-Academics/";
          
        },
      },{id: "post-what-phd-life-is-really-like",
        
          title: "What PhD Life is Really Like",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/What-PhD-Life-is-Really-Like/";
          
        },
      },{id: "post-the-workaholic-and-academia-in-defense-of-acadowntime",
        
          title: "The Workaholic and Academia: in defense of #AcaDowntime",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/The-Workaholic-and-Academia_-in-defense-of-AcaDowntime/";
          
        },
      },{id: "post-the-portrayal-of-academics-in-kids-books-a-chat-with-melissa-terras",
        
          title: "The Portrayal of Academics in Kids Books - a chat with Melissa Terras...",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/The-Portrayal-of-Academics-in-Kids-Books-a-chat-with-Melissa-Terras/";
          
        },
      },{id: "post-male-mad-and-muddleheaded-the-portrayal-of-academics-in-kids-books",
        
          title: "Male, Mad and Muddleheaded! The portrayal of academics in kids books",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/Male,-Mad-and-Muddleheaded!-The-portrayal-of-academics-in-kids-books/";
          
        },
      },{id: "post-academia-survival-of-the-bitterest",
        
          title: "Academia: Survival of the Bitterest?",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/Academia_-Survival-of-the-Bitterest/";
          
        },
      },{id: "post-academics-with-beer",
        
          title: "Academics with BEER!",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/Academics-with-BEER!/";
          
        },
      },{id: "post-academic-nursery-rhymes",
        
          title: "Academic Nursery Rhymes",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/Academic-Nursery-Rhymes/";
          
        },
      },{id: "post-is-this-the-worst-academic-journal-ever",
        
          title: "Is This the Worst Academic Journal Ever?",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/Is-This-the-Worst-Academic-Journal-Ever/";
          
        },
      },{id: "post-medieval-marginalia-reimagined-by-modern-academics",
        
          title: "Medieval Marginalia, Reimagined by Modern Academics",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/Medieval-Marginalia,-Reimagined-by-Modern-Academics/";
          
        },
      },{id: "post-ocean-energy-key-legal-issues-and-challenges",
        
          title: "Ocean Energy: key legal issues and challenges",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/Ocean-Energy_-key-legal-issues-and-challenges/";
          
        },
      },{id: "post-fun-and-laughter-in-the-lab",
        
          title: "Fun and Laughter in the Lab",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/Fun-and-Laughter-in-the-Lab/";
          
        },
      },{id: "post-why-does-it-always-rain-on-me-academics-forecast-their-day",
        
          title: "Why does it always rain on me? Academics forecast their day",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/Why-does-it-always-rain-on-me_-Academics-forecast-their-day/";
          
        },
      },{id: "post-cars-on-campus-rooftops-and-r2d2-observatories-6-awesome-college-pranks",
        
          title: "Cars on Campus Rooftops and R2D2 Observatories: 6 awesome college pranks",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/Cars-on-Campus-Rooftops-and-R2D2-Observatories_-6-awesome-college-pranks/";
          
        },
      },{id: "post-the-phd-path-less-travelled-share-your-story",
        
          title: "The PhD Path Less Travelled: share your story!",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/The-PhD-Path-Less-Travelled_-share-your-story!/";
          
        },
      },{id: "post-11-things-i-learned-about-academia-by-analysing-14-million-ratemyprofessor-reviews",
        
          title: "11 things I learned about academia by analysing 14 million RateMyProfessor reviews ",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/11-things-I-learned-about-academia-by-analysing-14-million-RateMyProfessor-reviews/";
          
        },
      },{id: "post-after-almost-10-years-progress-towards-new-agreement-on-high-seas",
        
          title: "After almost 10 years, progress towards new agreement on high seas",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/After-almost-10-years,-progress-towards-new-agreement-on-high-seas/";
          
        },
      },{id: "post-academics-with-cats-awards-cats-with-computers",
        
          title: "Academics with Cats Awards: Cats with Computers",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/Academics-with-Cats-Awards_-Cats-with-Computers/";
          
        },
      },{id: "post-academics-with-cats-awards-the-results-are-in",
        
          title: "Academics with Cats Awards: the results are in!",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/Academics-with-Cats-Awards_-the-results-are-in!/";
          
        },
      },{id: "post-a-day-in-the-life-of-an-academic-with-cats",
        
          title: "A Day in the Life of an Academic (with cats)",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2015/A-Day-in-the-Life-of-an-Academic-(with-cats)/";
          
        },
      },{id: "post-merry-christmas-and-an-academic-new-year",
        
          title: "Merry Christmas and an Academic New Year",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Merry-Christmas-and-an-Academic-New-Year/";
          
        },
      },{id: "post-what-do-academics-do-explained-with-cats",
        
          title: "What do Academics Do? (explained with cats)",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/What-do-Academics-Do_-(explained-with-cats)/";
          
        },
      },{id: "post-academic-cats-storify",
        
          title: "Academic Cats (storify)",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Academic-Cats-(storify)/";
          
        },
      },{id: "post-food-glorious-food",
        
          title: "Food, Glorious Food",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Food,-Glorious-Food/";
          
        },
      },{id: "post-the-first-annual-academics-in-hats-awards",
        
          title: "The First Annual Academics In Hats Awards",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/The-First-Annual-Academics-In-Hats-Awards/";
          
        },
      },{id: "post-this-post-is-intentionally-left-blank",
        
          title: "This Post is Intentionally Left Blank",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/This-Post-is-Intentionally-Left-Blank/";
          
        },
      },{id: "post-toilet-humour",
        
          title: "Toilet Humour",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Toilet-Humour/";
          
        },
      },{id: "post-10-comic-chemicals-presented-by-chemistry-cat",
        
          title: "10 Comic Chemicals, presented by Chemistry Cat",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/10-Comic-Chemicals,-presented-by-Chemistry-Cat/";
          
        },
      },{id: "post-i-ll-put-the-kettle-on-the-academic-39-s-guide-to-making-the-perfect-cuppa",
        
          title: "I’ll Put the Kettle On: the academic&#39;s guide to making the perfect cuppa...",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/I-ll-Put-the-Kettle-On_-the-academic&-039;s-guide-to-making-the-perfect-cuppa/";
          
        },
      },{id: "post-beards-in-academia-part-ii-more-popular-than-ever-beards-and-masculinity-in-history",
        
          title: "Beards in Academia, Part II: More Popular than Ever? Beards and Masculinity in...",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Beards-in-Academia,-Part-II_-More-Popular-than-Ever_-Beards-and-Masculinity-in-History/";
          
        },
      },{id: "post-proof-that-academia-is-teeming-with-humour-wit-and-general-oddness",
        
          title: "Proof that academia is teeming with humour, wit… and general oddness",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Proof-that-academia-is-teeming-with-humour,-wit-and-general-oddness/";
          
        },
      },{id: "post-food-glorious-food",
        
          title: "Food, Glorious Food!",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Food,-Glorious-Food!/";
          
        },
      },{id: "post-beards-in-academia",
        
          title: "Beards in Academia",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Beards-in-Academia/";
          
        },
      },{id: "post-top-10-hashtags-for-academics",
        
          title: "Top 10 hashtags for academics",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Top-10-hashtags-for-academics/";
          
        },
      },{id: "post-10-offbeat-university-buildings",
        
          title: "10 Offbeat University Buildings",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/10-Offbeat-University-Buildings/";
          
        },
      },{id: "post-finish-that-phd-in-12-simple-steps",
        
          title: "Finish that PhD in 12 Simple Steps!",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Finish-that-PhD-in-12-Simple-Steps!/";
          
        },
      },{id: "post-quirky-university-architecture",
        
          title: "Quirky University Architecture",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Quirky-University-Architecture/";
          
        },
      },{id: "post-5-more-ultra-modern-university-buildings",
        
          title: "5 More Ultra Modern University Buildings",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/5-More-Ultra-Modern-University-Buildings/";
          
        },
      },{id: "post-5-super-specific-academic-journals",
        
          title: "5 Super Specific Academic Journals",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/5-Super-Specific-Academic-Journals/";
          
        },
      },{id: "post-penguins",
        
          title: "Penguins",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Penguins/";
          
        },
      },{id: "post-footnotes",
        
          title: "Footnotes",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Footnotes/";
          
        },
      },{id: "post-bored-or-high-3-panda-death",
        
          title: "Bored or High? #3: Panda death",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Bored-or-High_-3_-Panda-death/";
          
        },
      },{id: "post-top-10-honest-job-ads",
        
          title: "Top 10 Honest Job Ads",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Top-10-Honest-Job-Ads/";
          
        },
      },{id: "post-monday-morning-meme-4",
        
          title: "Monday Morning Meme (4)",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Monday-Morning-Meme-(4)/";
          
        },
      },{id: "post-bored-or-high-4-urinal-dynamics",
        
          title: "Bored or High? #4: urinal dynamics",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Bored-or-High_-4_-urinal-dynamics/";
          
        },
      },{id: "post-monday-morning-meme",
        
          title: "Monday Morning Meme",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Monday-Morning-Meme/";
          
        },
      },{id: "post-bored-or-high-2-walking-on-water",
        
          title: "Bored or High? #2: walking on water",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Bored-or-High_-2_-walking-on-water/";
          
        },
      },{id: "post-bored-or-high-1-string-theory",
        
          title: "Bored or High? #1: string theory",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Bored-or-High_-1_-string-theory/";
          
        },
      },{id: "post-monday-morning-meme-3",
        
          title: "Monday Morning Meme (3)",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Monday-Morning-Meme-(3)/";
          
        },
      },{id: "post-coming-soon",
        
          title: "Coming soon!",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Coming-soon!/";
          
        },
      },{id: "post-amazing-acknowledgements-in-academic-papers",
        
          title: "Amazing Acknowledgements in Academic Papers",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Amazing-Acknowledgements-in-Academic-Papers/";
          
        },
      },{id: "post-co-authoring-now-with-60-more-croquet",
        
          title: "Co-authoring: Now with 60% more croquet!",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Co-authoring_-Now-with-60-more-croquet!/";
          
        },
      },{id: "post-monday-morning-meme-2",
        
          title: "Monday Morning Meme (2)",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Monday-Morning-Meme-(2)/";
          
        },
      },{id: "post-who-39-s-a-clever-boy-animals-in-academia",
        
          title: "Who&#39;s a clever boy? Animals in academia",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/&quot;Who&-039;s-a-clever-boy_&quot;-Animals-in-academia/";
          
        },
      },{id: "post-the-last-writes-posthumous-publishing",
        
          title: "The Last Writes: posthumous publishing",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/The-Last-Writes_-posthumous-publishing/";
          
        },
      },{id: "post-monday-morning-meme-1",
        
          title: "Monday Morning Meme (1)",
        
        description: "A humorous academic meme about the Monday morning experience in academia",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/Monday-Morning-Meme-(1)/";
          
        },
      },{id: "post-an-update-from-the-bbnj-working-group",
        
          title: "An update from the BBNJ working group",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/An-update-from-the-BBNJ-working-group/";
          
        },
      },{id: "post-european-commission-to-focus-on-marine-renewables",
        
          title: "European Commission to Focus on Marine Renewables",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2014/European-Commission-to-Focus-on-Marine-Renewables/";
          
        },
      },{id: "post-marine-governance-in-an-industrialised-ocean",
        
          title: "Marine Governance in an Industrialised Ocean",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2013/Marine-Governance-in-an-Industrialised-Ocean/";
          
        },
      },{id: "post-irena-in-the-global-energy-governance-context",
        
          title: "IRENA in the Global Energy Governance context",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2013/IRENA-in-the-Global-Energy-Governance-context/";
          
        },
      },{id: "post-peak-demand-targets-are-good-practice",
        
          title: "Peak Demand: Targets are Good Practice",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2013/Peak-Demand_-Targets-are-Good-Practice/";
          
        },
      },{id: "post-reducing-peak-demand-lowering-prices-but-what-about-emissions",
        
          title: "Reducing peak demand: lowering prices, but what about emissions?",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2013/Reducing-peak-demand_-lowering-prices,-but-what-about-emissions/";
          
        },
      },{id: "post-deployment-of-marine-renewables-some-thoughts-on-precaution-and-risk",
        
          title: "Deployment of Marine Renewables: some thoughts on precaution and risk",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2013/Deployment-of-Marine-Renewables_-some-thoughts-on-precaution-and-risk/";
          
        },
      },{id: "post-the-rochdale-envelope",
        
          title: "The Rochdale Envelope",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2012/The-Rochdale-Envelope/";
          
        },
      },{id: "post-regulating-marine-renewable-energy-a-brief-literature-review",
        
          title: "Regulating Marine Renewable Energy: a brief literature review",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2012/Regulating-Marine-Renewable-Energy_-a-brief-literature-review/";
          
        },
      },{id: "post-the-rising-tide-recent-global-developments-in-marine-renewable-energy",
        
          title: "The Rising Tide: recent global developments in marine renewable energy",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2012/The-Rising-Tide_-recent-global-developments-in-marine-renewable-energy/";
          
        },
      },{id: "post-marine-renewable-energy-in-australia-the-urgent-need-for-regulatory-reform",
        
          title: "Marine Renewable Energy in Australia: the urgent need for regulatory reform",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2012/Marine-Renewable-Energy-in-Australia_-the-urgent-need-for-regulatory-reform/";
          
        },
      },{id: "post-a-delegação-da-universidade-nacional-da-austrália-para-rio-20",
        
          title: "A Delegação da Universidade Nacional da Austrália para Rio +20",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2012/A-Delega%C3%A7%C3%A3o-da-Universidade-Nacional-da-Austr%C3%A1lia-para-Rio-+20/";
          
        },
      },{id: "post-marine-biodiversity-post-rio-20-towards-an-unclos-implementing-agreement",
        
          title: "Marine Biodiversity post-Rio+20: Towards an UNCLOS Implementing Agreement",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2012/Marine-Biodiversity-post-Rio+20_-Towards-an-UNCLOS-Implementing-Agreement/";
          
        },
      },{id: "post-rio-20-the-end-of-the-road",
        
          title: "Rio+20, The End of the Road",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2012/Rio+20,-The-End-of-the-Road/";
          
        },
      },{id: "post-high-hopes-for-fossil-fuel-subsidies-dashed-at-rio-20",
        
          title: "High Hopes for Fossil Fuel Subsidies Dashed at Rio+20",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2012/High-Hopes-for-Fossil-Fuel-Subsidies-Dashed-at-Rio+20/";
          
        },
      },{id: "post-rio-20-lacking-on-energy",
        
          title: "Rio+20 Lacking on Energy",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2012/Rio+20-Lacking-on-Energy/";
          
        },
      },{id: "post-the-future-we-definitely-don-t-want",
        
          title: "The Future we (Definitely Don’t) Want",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2012/The-Future-we-(Definitely-Don-t)-Want/";
          
        },
      },{id: "post-rio-20-negotiating-text-energy",
        
          title: "Rio+20 Negotiating Text: Energy",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2012/Rio+20-Negotiating-Text_-Energy/";
          
        },
      },{id: "post-rio-20-crucial-summit-hard-times",
        
          title: "Rio+20: crucial summit, hard times",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2012/Rio+20_-crucial-summit,-hard-times/";
          
        },
      },{id: "post-strategic-environmental-assessment-and-marine-renewable-energy-some-insights-from-iaia12",
        
          title: "Strategic Environmental Assessment and Marine Renewable Energy: some insights from IAIA12",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2012/Strategic-Environmental-Assessment-and-Marine-Renewable-Energy_-some-insights-from-IAIA12/";
          
        },
      },{id: "post-marine-renewable-energy-at-the-all-energy-expo",
        
          title: "Marine Renewable Energy at the All-Energy Expo",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2012/Marine-Renewable-Energy-at-the-All-Energy-Expo/";
          
        },
      },{id: "post-sustainable-development-the-energy-challenge",
        
          title: "Sustainable Development: the Energy Challenge",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2012/Sustainable-Development_-the-Energy-Challenge/";
          
        },
      },{id: "post-international-conference-on-the-environmental-interactions-of-marine-renewable-energy-technologies",
        
          title: "International Conference on the Environmental Interactions of Marine Renewable Energy Technologies",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2012/International-Conference-on-the-Environmental-Interactions-of-Marine-Renewable-Energy-Technologies/";
          
        },
      },{id: "post-reforming-the-nem-discussions-at-the-first-australian-energy-efficiency-summer-study",
        
          title: "Reforming the NEM: Discussions at the First Australian Energy Efficiency Summer Study",
        
        description: "",
        section: "Posts",
        handler: () => {
          
            window.location.href = "/blog/2012/Reforming-the-NEM_-Discussions-at-the-First-Australian-Energy-Efficiency-Summer-Study/";
          
        },
      },{id: "books-1q84",
          title: '1Q84',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/1q84/";
            },},{id: "books-21-lessons-for-the-21st-century",
          title: '21 Lessons for the 21st Century',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/21-lessons-for-the-21st-century/";
            },},{id: "books-a-conversation-at-the-end-of-the-world",
          title: 'A Conversation at the End of the World',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/a-conversation-at-the-end-of-the-world/";
            },},{id: "books-a-field-guide-to-getting-lost",
          title: 'A Field Guide to Getting Lost',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/a-field-guide-to-getting-lost/";
            },},{id: "books-a-general-theory-of-love",
          title: 'A General Theory of Love',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/a-general-theory-of-love/";
            },},{id: "books-academia-obscura",
          title: 'Academia Obscura',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/academia-obscura/";
            },},{id: "books-adult-children-of-alcoholics",
          title: 'Adult Children of Alcoholics',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/adult-children-of-alcoholics/";
            },},{id: "books-after-dark",
          title: 'After Dark',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/after-dark/";
            },},{id: "books-ambient-findability-what-we-find-changes-who-we-become",
          title: 'Ambient Findability: What We Find Changes Who We Become',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/ambient_findability/";
            },},{id: "books-atlas-obscura-an-explorer-39-s-guide-to-the-world-39-s-hidden-wonders",
          title: 'Atlas Obscura: An Explorer&amp;#39;s Guide to the World&amp;#39;s Hidden Wonders',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/atlas-obscura-an-explorers-guide-to-the-worlds-hidden-wonders/";
            },},{id: "books-being-ecological",
          title: 'Being Ecological',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/being-ecological/";
            },},{id: "books-being-mortal-medicine-and-what-matters-in-the-end",
          title: 'Being Mortal: Medicine and What Matters in the End',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/being-mortal-medicine-and-what-matters-in-the-end/";
            },},{id: "books-beyond-addiction-how-science-and-kindness-help-people-change",
          title: 'Beyond Addiction: How Science and Kindness Help People Change',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/beyond-addiction-how-science-and-kindness-help-people-change/";
            },},{id: "books-bird-by-bird-some-instructions-on-writing-and-life",
          title: 'Bird by Bird: Some Instructions on Writing and Life',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/bird-by-bird-some-instructions-on-writing-and-life/";
            },},{id: "books-brave-new-world",
          title: 'Brave New World',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/brave-new-world/";
            },},{id: "books-calypso",
          title: 'Calypso',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/calypso/";
            },},{id: "books-catch-22",
          title: 'Catch-22',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/catch-22/";
            },},{id: "books-che-the-diaries-of-ernesto-che-guevara",
          title: 'Che: The Diaries of Ernesto Che Guevara',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/che-the-diaries-of-ernesto-che-guevara/";
            },},{id: "books-collapse-how-societies-choose-to-fail-or-succeed",
          title: 'Collapse: How Societies Choose to Fail or Succeed',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/collapse-how-societies-choose-to-fail-or-succeed/";
            },},{id: "books-darwin-portrait-of-a-genius",
          title: 'Darwin: Portrait of a Genius',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/darwin-portrait-of-a-genius/";
            },},{id: "books-delta-of-venus",
          title: 'Delta of Venus',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/delta-of-venus/";
            },},{id: "books-flights",
          title: 'Flights',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/flights/";
            },},{id: "books-from-dusk-39-til-dawn-an-insider-39-s-view-of-the-growth-of-the-animal-liberation-movement",
          title: 'From Dusk &amp;#39;Til Dawn: An Insider&amp;#39;s View of the Growth of the Animal...',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/from-dusk-til-dawn-an-insiders-view-of-the-growth-of-the-animal-liberation-movement/";
            },},{id: "books-guns-germs-and-steel-the-fates-of-human-societies",
          title: 'Guns, Germs, and Steel: The Fates of Human Societies',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/guns-germs-and-steel-the-fates-of-human-societies/";
            },},{id: "books-heat-how-we-can-stop-the-planet-burning",
          title: 'Heat: How We Can Stop the Planet Burning',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/heat-how-we-can-stop-the-planet-burning/";
            },},{id: "books-homo-deus-a-history-of-tomorrow",
          title: 'Homo Deus: A History of Tomorrow',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/homo-deus-a-history-of-tomorrow/";
            },},{id: "books-how-to-change-your-mind-what-the-new-science-of-psychedelics-teaches-us-about-consciousness-dying-addiction-depression-and-transcendence",
          title: 'How to Change Your Mind: What the New Science of Psychedelics Teaches Us...',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/how-to-change-your-mind-what-the-new-science-of-psychedelics-teaches-us-about-consciousness-dying-ad/";
            },},{id: "books-how-to-travel-with-a-salmon-and-other-essays",
          title: 'How to Travel with a Salmon and Other Essays',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/how-to-travel-with-a-salmon-and-other-essays/";
            },},{id: "books-human-universe",
          title: 'Human Universe',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/human-universe/";
            },},{id: "books-i-burn-paris",
          title: 'I Burn Paris',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/i-burn-paris/";
            },},{id: "books-in-praise-of-idleness-and-other-essays",
          title: 'In Praise of Idleness and Other Essays',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/in-praise-of-idleness-and-other-essays/";
            },},{id: "books-incognito-the-secret-lives-of-the-brain",
          title: 'Incognito: The Secret Lives of the Brain',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/incognito-the-secret-lives-of-the-brain/";
            },},{id: "books-lincoln-in-the-bardo",
          title: 'Lincoln in the Bardo',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/lincoln-in-the-bardo/";
            },},{id: "books-logicomix-an-epic-search-for-truth",
          title: 'Logicomix: An Epic Search for Truth',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/logicomix-an-epic-search-for-truth/";
            },},{id: "books-maphead-charting-the-wide-weird-world-of-geography-wonks",
          title: 'Maphead: Charting the Wide, Weird World of Geography Wonks',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/maphead-charting-the-wide-weird-world-of-geography-wonks/";
            },},{id: "books-meditations",
          title: 'Meditations',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/meditations/";
            },},{id: "books-meltdown-iceland-how-the-global-financial-crisis-bankupted-an-entire-country",
          title: 'Meltdown Iceland: How The Global Financial Crisis Bankupted An Entire Country',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/meltdown-iceland-how-the-global-financial-crisis-bankupted-an-entire-country/";
            },},{id: "books-memoirs-of-a-polar-bear",
          title: 'Memoirs of a Polar Bear',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/memoirs-of-a-polar-bear/";
            },},{id: "books-men-at-arms",
          title: 'Men at Arms',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/men-at-arms/";
            },},{id: "books-monkeyluv-and-other-essays-on-our-lives-as-animals",
          title: 'Monkeyluv: And Other Essays on Our Lives as Animals',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/monkeyluv-and-other-essays-on-our-lives-as-animals/";
            },},{id: "books-more-than-two-a-practical-guide-to-ethical-polyamory",
          title: 'More Than Two: A Practical Guide to Ethical Polyamory',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/more-than-two-a-practical-guide-to-ethical-polyamory/";
            },},{id: "books-murder-in-samarkand-a-british-ambassador-39-s-controversial-defiance-of-tyranny-in-the-war-on-terror",
          title: 'Murder in Samarkand: A British Ambassador&amp;#39;s Controversial Defiance of Tyranny in the War...',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/murder-in-samarkand-a-british-ambassadors-controversial-defiance-of-tyranny-in-the-war-on-terror/";
            },},{id: "books-night-falls-fast-understanding-suicide",
          title: 'Night Falls Fast: Understanding Suicide',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/night-falls-fast-understanding-suicide/";
            },},{id: "books-no-logo",
          title: 'No Logo',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/no-logo/";
            },},{id: "books-norwegian-wood",
          title: 'Norwegian Wood',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/norwegian-wood/";
            },},{id: "books-on-writing-well-the-classic-guide-to-writing-nonfiction",
          title: 'On Writing Well: The Classic Guide to Writing Nonfiction',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/on-writing-well-the-classic-guide-to-writing-nonfiction/";
            },},{id: "books-opening-up-a-guide-to-creating-and-sustaining-open-relationships",
          title: 'Opening Up: A Guide to Creating and Sustaining Open Relationships',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/opening-up-a-guide-to-creating-and-sustaining-open-relationships/";
            },},{id: "books-orkneyinga-saga-the-history-of-the-earls-of-orkney",
          title: 'Orkneyinga Saga: The History of the Earls of Orkney',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/orkneyinga-saga-the-history-of-the-earls-of-orkney/";
            },},{id: "books-pais-bajo-mi-piel-el",
          title: 'PAIS BAJO MI PIEL, EL',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/pais-bajo-mi-piel-el/";
            },},{id: "books-philosophy-of-law-a-very-short-introduction",
          title: 'Philosophy of Law: A Very Short Introduction',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/philosophy-of-law-a-very-short-introduction/";
            },},{id: "books-poems-1962-2012",
          title: 'Poems 1962-2012',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/poems-1962-2012/";
            },},{id: "books-psycho-logical",
          title: 'Psycho-logical',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/psycho-logical/";
            },},{id: "books-rendering-in-pen-and-ink-the-classic-book-on-pen-and-ink-techniques-for-artists-illustrators-architects-and-designers",
          title: 'Rendering in Pen and Ink: The Classic Book on Pen and Ink Techniques...',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/rendering-in-pen-and-ink-the-classic-book-on-pen-and-ink-techniques-for-artists-illustrators-archite/";
            },},{id: "books-salt-a-world-history",
          title: 'Salt: A World History',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/salt-a-world-history/";
            },},{id: "books-sapiens-a-brief-history-of-humankind",
          title: 'Sapiens: A Brief History of Humankind',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/sapiens-a-brief-history-of-humankind/";
            },},{id: "books-science-sex-and-sacred-cows-spoofs-on-science-from-the-worm-runner-39-s-digest",
          title: 'Science, sex, and sacred cows;: Spoofs on science from the Worm runner&amp;#39;s digest...',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/science-sex-and-sacred-cows-spoofs-on-science-from-the-worm-runners-digest/";
            },},{id: "books-selected-cronicas",
          title: 'Selected Cronicas',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/selected-cronicas/";
            },},{id: "books-seneca-39-s-letters-from-a-stoic",
          title: 'Seneca&amp;#39;s Letters from a Stoic',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/senecas-letters-from-a-stoic/";
            },},{id: "books-sex-from-scratch-making-your-own-relationship-rules",
          title: 'Sex From Scratch: Making Your Own Relationship Rules',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/sex-from-scratch-making-your-own-relationship-rules/";
            },},{id: "books-siddhartha",
          title: 'Siddhartha',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/siddhartha/";
            },},{id: "books-six-easy-pieces-essentials-of-physics-by-its-most-brilliant-teacher",
          title: 'Six Easy Pieces: Essentials of Physics By Its Most Brilliant Teacher',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/six-easy-pieces-essentials-of-physics-by-its-most-brilliant-teacher/";
            },},{id: "books-snow-crash",
          title: 'Snow Crash',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/snow-crash/";
            },},{id: "books-steal-like-an-artist-10-things-nobody-told-you-about-being-creative",
          title: 'Steal Like an Artist: 10 Things Nobody Told You About Being Creative',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/steal-like-an-artist-10-things-nobody-told-you-about-being-creative/";
            },},{id: "books-still-life-with-woodpecker",
          title: 'Still Life with Woodpecker',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/still-life-with-woodpecker/";
            },},{id: "books-stories-and-prose-poems",
          title: 'Stories and Prose Poems',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/stories-and-prose-poems/";
            },},{id: "books-stress-analysis-of-a-strapless-evening-gown",
          title: 'Stress Analysis of a Strapless Evening Gown',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/stress-analysis-of-a-strapless-evening-gown/";
            },},{id: "books-sum-forty-tales-from-the-afterlives",
          title: 'Sum: Forty Tales from the Afterlives',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/sum-forty-tales-from-the-afterlives/";
            },},{id: "books-talking-to-strangers-what-we-should-know-about-the-people-we-don-39-t-know",
          title: 'Talking to Strangers: What We Should Know about the People We Don&amp;#39;t Know...',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/talking-to-strangers-what-we-should-know-about-the-people-we-dont-know/";
            },},{id: "books-tenth-of-december",
          title: 'Tenth of December',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/tenth-of-december/";
            },},{id: "books-the-4-hour-body-an-uncommon-guide-to-rapid-fat-loss-incredible-sex-and-becoming-superhuman",
          title: 'The 4-Hour Body: An Uncommon Guide to Rapid Fat-Loss, Incredible Sex, and Becoming...',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-4-hour-body-an-uncommon-guide-to-rapid-fat-loss-incredible-sex-and-becoming-superhuman/";
            },},{id: "books-the-alchemist",
          title: 'The Alchemist',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-alchemist/";
            },},{id: "books-the-argonauts",
          title: 'The Argonauts',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-argonauts/";
            },},{id: "books-the-art-and-zen-of-motorcycle-maintenance",
          title: 'The Art and Zen of Motorcycle Maintenance',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-art-and-zen-of-motorcycle-maintenance/";
            },},{id: "books-the-bell-jar",
          title: 'The Bell Jar',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-bell-jar/";
            },},{id: "books-the-birthday-of-the-world-and-other-stories",
          title: 'The Birthday of the World and Other Stories',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-birthday-of-the-world-and-other-stories/";
            },},{id: "books-the-body-artist",
          title: 'The Body Artist',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-body-artist/";
            },},{id: "books-the-bottom-billion-why-the-poorest-countries-are-failing-and-what-can-be-done-about-it",
          title: 'The Bottom Billion: Why the Poorest Countries Are Failing and What Can Be...',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-bottom-billion-why-the-poorest-countries-are-failing-and-what-can-be-done-about-it/";
            },},{id: "books-the-box-how-the-shipping-container-made-the-world-smaller-and-the-world-economy-bigger",
          title: 'The Box: How the Shipping Container Made the World Smaller and the World...',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-box-how-the-shipping-container-made-the-world-smaller-and-the-world-economy-bigger/";
            },},{id: "books-the-brief-and-frightening-reign-of-phil",
          title: 'The Brief and Frightening Reign of Phil',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-brief-and-frightening-reign-of-phil/";
            },},{id: "books-the-chairs-are-where-the-people-go-how-to-live-work-and-play-in-the-city",
          title: 'The Chairs Are Where the People Go: How to Live, Work, and Play...',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-chairs-are-where-the-people-go-how-to-live-work-and-play-in-the-city/";
            },},{id: "books-the-comprehensive-enfp-survival-guide",
          title: 'The Comprehensive ENFP Survival Guide',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-comprehensive-enfp-survival-guide/";
            },},{id: "books-the-ethical-slut-a-guide-to-infinite-sexual-possibilities",
          title: 'The Ethical Slut: A Guide to Infinite Sexual Possibilities',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-ethical-slut-a-guide-to-infinite-sexual-possibilities/";
            },},{id: "books-the-future-earth-a-radical-vision-for-what-39-s-possible-in-the-age-of-warming",
          title: 'The Future Earth: A Radical Vision for What&amp;#39;s Possible in the Age of...',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-future-earth-a-radical-vision-for-whats-possible-in-the-age-of-warming/";
            },},{id: "books-the-future-eaters-an-ecological-history-of-the-australasian-lands-and-people",
          title: 'The Future Eaters: An Ecological History of the Australasian Lands and People',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-future-eaters-an-ecological-history-of-the-australasian-lands-and-people/";
            },},{id: "books-the-groves-of-academe",
          title: 'The Groves of Academe',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-groves-of-academe/";
            },},{id: "books-the-ocean-of-life-the-fate-of-man-and-the-sea",
          title: 'The Ocean of Life: The Fate of Man and the Sea',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-ocean-of-life-the-fate-of-man-and-the-sea/";
            },},{id: "books-the-overstory",
          title: 'The Overstory',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-overstory/";
            },},{id: "books-the-principles-of-uncertainty",
          title: 'The Principles of Uncertainty',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-principles-of-uncertainty/";
            },},{id: "books-the-selfish-gene",
          title: 'The Selfish Gene',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-selfish-gene/";
            },},{id: "books-the-serendipity-foundation",
          title: 'The Serendipity Foundation',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-serendipity-foundation/";
            },},{id: "books-the-tipping-point-how-little-things-can-make-a-big-difference",
          title: 'The Tipping Point: How Little Things Can Make a Big Difference',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the-tipping-point-how-little-things-can-make-a-big-difference/";
            },},{id: "books-thinking-basketball",
          title: 'Thinking Basketball',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/thinking-basketball/";
            },},{id: "books-this-changes-everything-capitalism-vs-the-climate",
          title: 'This Changes Everything: Capitalism vs. The Climate',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/this-changes-everything-capitalism-vs-the-climate/";
            },},{id: "books-this-other-eden",
          title: 'This Other Eden',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/this-other-eden/";
            },},{id: "books-utopia-for-realists",
          title: 'Utopia for Realists',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/utopia-for-realists/";
            },},{id: "books-why-we-sleep-unlocking-the-power-of-sleep-and-dreams",
          title: 'Why We Sleep: Unlocking the Power of Sleep and Dreams',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/why-we-sleep-unlocking-the-power-of-sleep-and-dreams/";
            },},{id: "books-wild-law",
          title: 'Wild Law',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/wild-law/";
            },},{id: "books-wild-ones-a-sometimes-dismaying-weirdly-reassuring-story-about-looking-at-people-looking-at-animals-in-america",
          title: 'Wild Ones: A Sometimes Dismaying, Weirdly Reassuring Story About Looking at People Looking...',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/wild-ones-a-sometimes-dismaying-weirdly-reassuring-story-about-looking-at-people-looking-at-animals-/";
            },},{id: "creative-belles-parentheses",
          title: 'belles parentheses',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/belles-parentheses/";
            },},{id: "creative-ignorance-is-bliss",
          title: 'ignorance is bliss',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/ignorance-is-bliss/";
            },},{id: "creative-escape",
          title: 'escape',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/escape/";
            },},{id: "creative-restart",
          title: 'restart',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/restart/";
            },},{id: "creative-return",
          title: 'return',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/return/";
            },},{id: "creative-flamingo-i",
          title: 'flamingo I',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/flamingo-i/";
            },},{id: "creative-flamingo-ii",
          title: 'flamingo II',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/flamingo-ii/";
            },},{id: "creative-flamingos-iii",
          title: 'flamingos III',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/flamingos-iii/";
            },},{id: "creative-flamingos-vi",
          title: 'flamingos VI',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/flamingos-vi/";
            },},{id: "creative-better-late-than-never",
          title: 'better late than never',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/better-late-than-never/";
            },},{id: "creative-commercial-refrigerator",
          title: 'commercial refrigerator',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/commercial-refrigerator/";
            },},{id: "creative-fog-lifting",
          title: 'fog lifting',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/fog-lifting/";
            },},{id: "creative-gas-station",
          title: 'gas station',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/gas-station/";
            },},{id: "creative-generally-uncanny",
          title: 'generally uncanny',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/generally-uncanny/";
            },},{id: "creative-in-the-context",
          title: 'in the context',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/in-the-context/";
            },},{id: "creative-pint-of-best",
          title: 'pint of best',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/pint-of-best/";
            },},{id: "creative-self",
          title: 'self',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/self/";
            },},{id: "creative-tanks",
          title: 'tanks',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/tanks/";
            },},{id: "creative-transcend-bullshit",
          title: 'transcend bullshit',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/transcend-bullshit/";
            },},{id: "creative-devastatingly-alone",
          title: 'devastatingly alone',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/devastatingly-alone/";
            },},{id: "creative-good-news",
          title: 'good news',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/good-news/";
            },},{id: "creative-loop",
          title: 'loop',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/loop/";
            },},{id: "creative-normal-oligarchs",
          title: 'normal oligarchs',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/normal-oligarchs/";
            },},{id: "creative-the-void",
          title: 'the void',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/the-void/";
            },},{id: "creative-commercial-white",
          title: 'commercial white',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/commercial-white/";
            },},{id: "creative-downpour",
          title: 'downpour',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/downpour/";
            },},{id: "creative-my-alibi",
          title: 'my alibi',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/my-alibi/";
            },},{id: "creative-night-watch",
          title: 'night watch',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/night-watch/";
            },},{id: "creative-roller-coaster",
          title: 'roller coaster',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/roller-coaster/";
            },},{id: "creative-silvery-moon",
          title: 'silvery moon',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/silvery-moon/";
            },},{id: "creative-stone-39-s-throw",
          title: 'stone&amp;#39;s throw',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/stones-throw/";
            },},{id: "creative-bad-idea",
          title: 'bad idea',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/bad-idea/";
            },},{id: "creative-individuals-suffer",
          title: 'individuals suffer',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/individuals-suffer/";
            },},{id: "creative-ancient-landscape",
          title: 'ancient landscape',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/ancient-landscape/";
            },},{id: "creative-dead-people-don-39-t-move",
          title: 'dead people don&amp;#39;t move',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/dead-people-dont-move/";
            },},{id: "creative-further-radicalize",
          title: 'further radicalize',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/further-radicalize/";
            },},{id: "creative-industrial-production",
          title: 'industrial production',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/industrial-production/";
            },},{id: "creative-intense-spaces",
          title: 'intense spaces',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/intense-spaces/";
            },},{id: "creative-we-shall-not-cease",
          title: 'we shall not cease',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/we-shall-not-cease/";
            },},{id: "creative-are-we-alone",
          title: 'are we alone',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/are-we-alone/";
            },},{id: "creative-around-the-corner",
          title: 'around the corner',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/around-the-corner/";
            },},{id: "creative-attempting-to-survive",
          title: 'attempting to survive',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/attempting-to-survive/";
            },},{id: "creative-canal-mania",
          title: 'canal mania',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/canal-mania/";
            },},{id: "creative-cannabis",
          title: 'cannabis',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/cannabis/";
            },},{id: "creative-dress-informal",
          title: 'dress informal',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/dress-informal/";
            },},{id: "creative-end",
          title: 'end',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/end/";
            },},{id: "creative-extends-absurdly",
          title: 'extends absurdly',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/extends-absurdly/";
            },},{id: "creative-ghost-station",
          title: 'ghost station',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/ghost-station/";
            },},{id: "creative-juvenile-turtles",
          title: 'juvenile turtles',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/juvenile-turtles/";
            },},{id: "creative-leather-shoes",
          title: 'leather shoes',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/leather-shoes/";
            },},{id: "creative-mimetic-animals",
          title: 'mimetic animals',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/mimetic-animals/";
            },},{id: "creative-pop-art",
          title: 'pop art',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/pop-art/";
            },},{id: "creative-pretty-airplane",
          title: 'pretty airplane',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/pretty-airplane/";
            },},{id: "creative-returned-to-earth",
          title: 'returned to earth',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/returned-to-earth/";
            },},{id: "creative-seaside",
          title: 'seaside',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/seaside/";
            },},{id: "creative-tasting-board",
          title: 'tasting board',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/tasting-board/";
            },},{id: "creative-therefore-i-am",
          title: 'therefore i am',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/therefore-i-am/";
            },},{id: "creative-to-go-out",
          title: 'to go out',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/to-go-out/";
            },},{id: "creative-to-live",
          title: 'to live',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/to-live/";
            },},{id: "creative-to-swim",
          title: 'to swim',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/to-swim/";
            },},{id: "creative-to-worry",
          title: 'to worry',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/to-worry/";
            },},{id: "creative-where-are-we",
          title: 'where are we',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/where-are-we/";
            },},{id: "creative-who-are-we",
          title: 'who are we',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/who-are-we/";
            },},{id: "creative-why-are-we-here",
          title: 'why are we here',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/why-are-we-here/";
            },},{id: "creative-disc-usa",
          title: 'disc USA',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/disc-usa/";
            },},{id: "creative-four-seasons-in-one-day",
          title: 'four seasons in one day',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/four-seasons-in-one-day/";
            },},{id: "creative-half-the-world-i",
          title: 'half the world I',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/half-the-world-i/";
            },},{id: "creative-half-the-world-ii",
          title: 'half the world II',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/half-the-world-ii/";
            },},{id: "creative-with-or-without-you",
          title: 'with or without you',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/with-or-without-you/";
            },},{id: "creative-yellow",
          title: 'yellow',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/yellow/";
            },},{id: "creative-death-is-inevitable",
          title: 'death is inevitable',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/death-is-inevitable/";
            },},{id: "creative-i-dont-think",
          title: 'i dont think',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/i-dont-think/";
            },},{id: "creative-one-pretends",
          title: 'one pretends',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/one-pretends/";
            },},{id: "creative-paradoxe",
          title: 'paradoxe',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/paradoxe/";
            },},{id: "creative-seduits",
          title: 'seduits',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/seduits/";
            },},{id: "creative-drugstore",
          title: 'drugstore',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/drugstore/";
            },},{id: "creative-fight",
          title: 'fight',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/fight/";
            },},{id: "creative-kids",
          title: 'kids',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/kids/";
            },},{id: "creative-money",
          title: 'money',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/money/";
            },},{id: "creative-thoughts",
          title: 'thoughts',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/thoughts/";
            },},{id: "creative-withdrawn",
          title: 'withdrawn',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/withdrawn/";
            },},{id: "creative-door",
          title: 'door',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/door/";
            },},{id: "creative-hillside",
          title: 'hillside',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/hillside/";
            },},{id: "creative-pool",
          title: 'pool',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/pool/";
            },},{id: "creative-treat-yourself",
          title: 'treat yourself',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/treat-yourself/";
            },},{id: "creative-for-two",
          title: 'for two',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/for-two/";
            },},{id: "creative-ode",
          title: 'ode',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/ode/";
            },},{id: "creative-pause",
          title: 'pause',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/pause/";
            },},{id: "creative-so-melodramatic",
          title: 'so melodramatic!',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/so-melodramatic/";
            },},{id: "creative-before-it-is-all-over",
          title: 'before it is all over',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/before-it-is-all-over/";
            },},{id: "creative-schrodingers-bullshitter",
          title: 'schrodingers bullshitter',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/schrodingers-bullshitter/";
            },},{id: "creative-six-different-stories",
          title: 'six different stories',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/six-different-stories/";
            },},{id: "creative-take-a-look",
          title: 'take a look',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/take-a-look/";
            },},{id: "creative-feelings",
          title: 'feelings',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/feelings/";
            },},{id: "creative-getting-shit-done",
          title: 'getting shit done',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/getting-shit-done/";
            },},{id: "creative-hallucinant",
          title: 'hallucinant',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/hallucinant/";
            },},{id: "creative-on-est-ici",
          title: 'on est ici',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/on-est-ici/";
            },},{id: "creative-slice-of-heaven",
          title: 'slice of heaven',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/slice-of-heaven/";
            },},{id: "creative-climate-apocalypse-for-kids",
          title: 'climate apocalypse for kids',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/climate-apocalypse-for-kids/";
            },},{id: "creative-purposes-are-bullshit",
          title: 'purposes are bullshit',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/purposes-are-bullshit/";
            },},{id: "creative-the-privilege-of-freedom",
          title: 'the privilege of freedom',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/the-privilege-of-freedom/";
            },},{id: "creative-what-end",
          title: 'what end',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/what-end/";
            },},{id: "creative-what-happened",
          title: 'what happened',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/what-happened/";
            },},{id: "creative-what-is-the-point",
          title: 'what is the point',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/what-is-the-point/";
            },},{id: "creative-tour-du-table",
          title: 'tour du table',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/tour-du-table/";
            },},{id: "creative-contre-couru",
          title: 'contre-couru?',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/contre-couru/";
            },},{id: "creative-gush",
          title: 'Gush',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/gush/";
            },},{id: "creative-hike",
          title: 'hike',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/hike/";
            },},{id: "creative-invite",
          title: 'invite',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/invite/";
            },},{id: "creative-lost-keys",
          title: 'lost keys',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/lost-keys/";
            },},{id: "creative-on-making-time",
          title: 'on making time',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/on-making-time/";
            },},{id: "creative-sunday",
          title: 'sunday',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/sunday/";
            },},{id: "creative-talking-endlessly",
          title: 'talking endlessly',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/talking-endlessly/";
            },},{id: "creative-the-edge-of-the-desk",
          title: 'the edge of the desk',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/the-edge-of-the-desk/";
            },},{id: "creative-the-object-that-refuses-to-leave",
          title: 'the object that refuses to leave',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/the-object-that-refuses-to-lea/";
            },},{id: "creative-white-amp-black",
          title: 'white &amp;amp; black',
          description: "",
          section: "Creative",handler: () => {
              window.location.href = "/creative/white-black/";
            },},{id: "library-climate-change-solutions-conference",
          title: 'Climate Change Solutions Conference',
          description: "Climate Change Solutions Conference",
          section: "Library",handler: () => {
              window.location.href = "/library/climate-change-solutions-conference/";
            },},{id: "library-student-protest-on-campus",
          title: 'Student Protest on Campus',
          description: "Student Protest on Campus",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-student-protest-campus/";
            },},{id: "library-fossil-fools-day",
          title: 'Fossil Fools Day',
          description: "Fossil Fools Day",
          section: "Library",handler: () => {
              window.location.href = "/library/fossil-fools-day/";
            },},{id: "library-carbon-offsets-and-consumer-protection",
          title: 'Carbon Offsets and Consumer Protection',
          description: "Carbon Offsets and Consumer Protection",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-carbon-offsets-consumer-protection/";
            },},{id: "library-designing-climate-law-a-comparative-analysis-of-the-us-and-eu",
          title: 'Designing Climate Law: A Comparative Analysis of the US and EU',
          description: "As evidence of anthropogenic climate change mounts there is a growing concern with, and a pressing need for, legal regimes to curtail the problem. This concern culminated in the recent climate change ...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-designing-climate-law-comparative-analysis-us-eu/";
            },},{id: "library-hart-s-concept-of-law-positivist-legal-theory-or-sociology",
          title: 'Hart’s Concept of Law: Positivist Legal Theory or Sociology?',
          description: "This paper will consider the extent to which HLA Hart can be said to have turned the positivist tradition of legal thought from positivism to a sociology of law. Hart&#39;s claim to be engaging in &#39;descri...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-harts-concept-law-positivist-legal-theory-sociology/";
            },},{id: "library-the-standard-of-reasonable-care-and-skill-expected-of-an-accountant",
          title: 'The Standard of Reasonable Care and Skill Expected of an Accountant',
          description: "The case concerns the standard of reasonable care and skill expected of an accountant, and the tests for causation, contributory negligence, and concurrent wrongdoing. The accountant in this case advi...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-standard-reasonable-care-skill-expected-accountant/";
            },},{id: "library-model-united-nations",
          title: 'Model United Nations',
          description: "Model United Nations",
          section: "Library",handler: () => {
              window.location.href = "/library/model-united-nations/";
            },},{id: "library-conceptualising-and-combating-transnational-environmental-crime",
          title: 'Conceptualising and combating transnational environmental crime',
          description: "To date, transnational environmental crime has been poorly attended to by the transnational organised crime and transnational policing discourse. Academics have focused on individual elements of envir...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-conceptualising-combating-transnational-environmental-crime/";
            },},{id: "library-marine-energy",
          title: 'Marine energy',
          description: "Marine energy",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-marine-energy/";
            },},{id: "library-your-flag-39-s-got-my-flag-on-it-the-union-jack-and-the-australian-flag",
          title: 'Your Flag&amp;#39;s Got My Flag On It: the Union Jack and the Australian...',
          description: "Your Flag&#39;s Got My Flag On It: the Union Jack and the Australian Flag",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-flags-got-flag-it-union-jack-australian-flag/";
            },},{id: "library-granting-of-leave-to-bring-derivative-proceedings-under-section-237-of-the-corporations-act",
          title: 'Granting of leave to bring derivative proceedings under section 237 of the Corporations...',
          description: "The Judge considered in detail whether there were serious questions to be tried under section 237(2)(d).The Judge held that claims that the companies in question had made loans to directors, &quot;alienate...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-granting-leave-bring-derivative-proceedings-section-237-corporations-act/";
            },},{id: "library-indigenous-people-and-customary-land-ownership-under-domestic-redd-frameworks-a-case-study-of-indonesia",
          title: 'Indigenous People and Customary Land Ownership Under Domestic REDD+ Frameworks: a case study...',
          description: "This paper aims to explore the interaction between domestic legal frameworks implementing the REDD+ mechanism and customary land ownership by using the regulatory regime of Indonesia as a case study. ...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-indigenous-people-customary-land-ownership-domestic-redd-frameworks-case-indonesia/";
            },},{id: "library-the-international-renewable-energy-agency-a-global-voice-for-the-renewable-energy-era",
          title: 'The International Renewable Energy Agency: A Global Voice for the Renewable Energy Era?...',
          description: "The International Renewable Energy Agency held the first session of its Assembly as a fully-fledged international organisation in April 2011. This article aims to introduce the Agency and provide a ba...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-international-renewable-energy-agency-global-voice-renewable-energy-era/";
            },},{id: "library-marine-energy-in-australia-and-new-zealand-regulatory-barriers-and-policy-measures",
          title: 'Marine Energy in Australia and New Zealand: Regulatory Barriers and Policy Measures',
          description: "Marine Energy in Australia and New Zealand: Regulatory Barriers and Policy Measures",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-marine-energy-australia-new-zealand-regulatory-barriers-policy-measures/";
            },},{id: "library-a-tidal-power-project",
          title: 'A Tidal Power Project',
          description: "A Tidal Power Project",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-tidal-power-project/";
            },},{id: "library-environmental-law-in-developing-countries-challenges-and-prospects",
          title: 'Environmental Law in Developing Countries: Challenges and Prospects',
          description: "Environmental Law in Developing Countries: Challenges and Prospects",
          section: "Library",handler: () => {
              window.location.href = "/library/environmental-law-developing-countries-challenges-prospects/";
            },},{id: "library-submission-to-the-australian-energy-market-commission-aemc-distribution-network-planning-and-expansion-framework-ministerial-council-on-energy-mce-rule-change-request",
          title: 'Submission to the Australian Energy Market Commission (AEMC): Distribution Network Planning and Expansion...',
          description: "Submission to the Australian Energy Market Commission (AEMC): Distribution Network Planning and Expa...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-submission-australian-energy-market-commission-aemc-distribution-network-planning-expansion-framework-ministerial-council-energy-mce-rule-change-request/";
            },},{id: "library-submission-to-the-australian-energy-market-commission-aemc-efficiency-benefit-sharing-scheme-and-demand-management-expenditure-by-transmission-businesses",
          title: 'Submission to the Australian Energy Market Commission (AEMC): Efficiency Benefit Sharing Scheme and...',
          description: "Submission to the Australian Energy Market Commission (AEMC): Efficiency Benefit Sharing Scheme and ...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-submission-australian-energy-market-commission-aemc-efficiency-benefit-sharing-scheme-demand-management-expenditure-transmission-businesses/";
            },},{id: "library-submission-to-the-australian-energy-market-commission-aemc-inclusion-of-embedded-generation-research-into-the-demand-management-incentive-scheme",
          title: 'Submission to the Australian Energy Market Commission (AEMC):Inclusion of Embedded Generation Research into...',
          description: "Submission to the Australian Energy Market Commission (AEMC):Inclusion of Embedded Generation Resear...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-submission-australian-energy-market-commission-aemc-inclusion-embedded-generation-research-demand-management-incentive-scheme/";
            },},{id: "library-submission-to-the-australian-energy-market-commission-aemc-national-electricity-amendment-total-factor-productivity-for-distribution-network-regulation-rule",
          title: 'Submission to the Australian Energy Market Commission (AEMC): National Electricity Amendment (Total Factor...',
          description: "Submission to the Australian Energy Market Commission (AEMC): National Electricity Amendment (Total ...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-submission-australian-energy-market-commission-aemc-national-electricity-amendment-total-factor-productivity-distribution-network-regulation-rule/";
            },},{id: "library-marine-renewable-energy-an-overview-of-applicable-australian-legistlation-and-regulatory-bodies",
          title: 'Marine Renewable Energy: an overview of applicable Australian legistlation and regulatory bodies',
          description: "Marine Renewable Energy: an overview of applicable Australian legistlation and regulatory bodies",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-marine-renewable-energy-overview-applicable-australian-legistlation-regulatory-bodies/";
            },},{id: "library-submission-to-the-australian-energy-market-commission-economic-regulation-of-network-service-providers-consultation-on-request-for-a-rule-change",
          title: 'Submission to the Australian Energy Market Commission: Economic Regulation of Network Service Providers...',
          description: "Submission to the Australian Energy Market Commission: Economic Regulation of Network Service Provid...",
          section: "Library",handler: () => {
              window.location.href = "/library/submission-australian-energy-market-commission-economic-regulation-network-service-providers-consultation-request-rule-change/";
            },},{id: "library-australian-national-university-student-delegation-to-rio-20",
          title: 'Australian National University student delegation to Rio+20',
          description: "Australian National University student delegation to Rio+20",
          section: "Library",handler: () => {
              window.location.href = "/library/australian-national-university-student-delegation-rio-20/";
            },},{id: "library-demand-management-targets-for-networks-in-the-national-electricity-market",
          title: 'Demand management targets for networks in the National Electricity Market',
          description: "Demand management targets for networks in the National Electricity Market",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-demand-management-targets-networks-national-electricity-market/";
            },},{id: "library-the-energy-challenge-renewables-at-rio-20",
          title: 'The Energy Challenge: Renewables at Rio+20',
          description: "The Energy Challenge: Renewables at Rio+20",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-energy-challenge-renewables-rio-20/";
            },},{id: "library-facilitating-efficient-augmentation-of-transmission-networks-to-connect-renewable-energy-generation-the-australian-experience",
          title: 'Facilitating efficient augmentation of transmission networks to connect renewable energy generation: the Australian...',
          description: "Facilitating efficient augmentation of transmission networks to connect renewable energy generation:...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-facilitating-efficient-augmentation-transmission-networks-connect-renewable-energy-generation-australian-experience/";
            },},{id: "library-marine-energy-designing-a-regulatory-framework-for-an-abundant-renewable-energy-resource-poster",
          title: 'Marine Energy: Designing a Regulatory Framework for an Abundant Renewable Energy Resource (Poster)...',
          description: "Marine Energy: Designing a Regulatory Framework for an Abundant Renewable Energy Resource (Poster)",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-marine-energy-designing-regulatory-framework-abundant-renewable-energy-resource-poster/";
            },},{id: "library-marine-renewable-energy-legal-and-policy-challenges-to-integrating-an-emerging-renewable-energy-source",
          title: 'Marine Renewable Energy: Legal and Policy Challenges to Integrating an Emerging Renewable Energy...',
          description: "Marine Renewable Energy: Legal and Policy Challenges to Integrating an Emerging Renewable Energy Sou...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-marine-renewable-energy-legal-policy-challenges-integrating-emerging-renewable-energy-source/";
            },},{id: "library-the-national-electricity-market-and-the-environment-are-we-heading-in-the-right-direction",
          title: 'The National Electricity Market and the Environment: Are we heading in the right...',
          description: "The National Electricity Market and the Environment: Are we heading in the right direction?",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-national-electricity-market-environment-heading-right-direction/";
            },},{id: "library-ngos-and-western-hegemony-causes-for-concern-and-ideas-for-change",
          title: 'NGOs and Western hegemony: causes for concern and ideas for change',
          description: "Since their rise to prominence in the post-World War II period, NGOs have grown exponentially in size and stature. This growth has occurred most notably under the New Policy Agenda, with Western donor...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-ngos-western-hegemony-causes-concern-ideas-change/";
            },},{id: "library-submission-to-the-australian-energy-market-commission-aemc-small-generation-aggregator-framework",
          title: 'Submission to the Australian Energy Market Commission (AEMC): Small Generation Aggregator Framework',
          description: "Submission to the Australian Energy Market Commission (AEMC): Small Generation Aggregator Framework",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-submission-australian-energy-market-commission-aemc-small-generation-aggregator-framework/";
            },},{id: "library-submission-to-the-australian-energy-regulator-review-of-limited-merits-review-regime",
          title: 'Submission to the Australian Energy Regulator: Review of Limited Merits Review Regime',
          description: "Submission to the Australian Energy Regulator: Review of Limited Merits Review Regime",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-submission-australian-energy-regulator-review-limited-merits-review-regime/";
            },},{id: "library-submission-to-the-australian-energy-market-commission-aemc-power-of-choice-review",
          title: 'Submission to the Australian Energy Market Commission (AEMC): Power of Choice Review',
          description: "Submission to the Australian Energy Market Commission (AEMC): Power of Choice Review",
          section: "Library",handler: () => {
              window.location.href = "/library/submission-australian-energy-market-commission-aemc-power-choice-review/";
            },},{id: "library-submission-to-the-australian-energy-regulator-powerlink-revenue-determination",
          title: 'Submission to the Australian Energy Regulator: Powerlink Revenue Determination',
          description: "Submission to the Australian Energy Regulator: Powerlink Revenue Determination",
          section: "Library",handler: () => {
              window.location.href = "/library/submission-australian-energy-regulator-powerlink-revenue-determination/";
            },},{id: "library-submission-to-council-of-australian-governors-regulatory-and-competition-reform",
          title: 'Submission to Council of Australian Governors: Regulatory and Competition Reform',
          description: "Submission to Council of Australian Governors: Regulatory and Competition Reform",
          section: "Library",handler: () => {
              window.location.href = "/library/submission-council-australian-governors-regulatory-competition-reform/";
            },},{id: "library-submission-to-the-department-of-climate-change-and-energy-efficiency-consultation-on-a-national-energy-savings-initiative",
          title: 'Submission to the Department of Climate Change and Energy Efficiency: Consultation on a...',
          description: "Submission to the Department of Climate Change and Energy Efficiency: Consultation on a national Ene...",
          section: "Library",handler: () => {
              window.location.href = "/library/submission-department-climate-change-energy-efficiency-consultation-national-energy-savings-initiative/";
            },},{id: "library-submission-to-the-public-accounts-committee-inquiry-into-the-economics-of-energy-generation",
          title: 'Submission to the Public Accounts Committee: Inquiry into the Economics of Energy Generation...',
          description: "Submission to the Public Accounts Committee: Inquiry into the Economics of Energy Generation",
          section: "Library",handler: () => {
              window.location.href = "/library/submission-public-accounts-committee-inquiry-economics-energy-generation/";
            },},{id: "library-marine-genetic-resources-in-areas-beyond-national-jurisdiction-an-annotated-bibliography",
          title: 'Marine Genetic Resources in Areas Beyond National Jurisdiction: an annotated bibliography',
          description: "Marine Genetic Resources in Areas Beyond National Jurisdiction: an annotated bibliography",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-marine-genetic-resources-areas-beyond-national-jurisdiction-annotated-bibliography/";
            },},{id: "library-systemic-biases-in-the-national-electricity-market-barriers-to-demand-side-participation",
          title: 'Systemic Biases in the National Electricity Market: Barriers to Demand-side Participation',
          description: "Systemic Biases in the National Electricity Market: Barriers to Demand-side Participation",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-systemic-biases-national-electricity-market-barriers-demand-side-participation/";
            },},{id: "library-marine-renewable-energy-effectively-balancing-the-needs-of-developers-and-potential-environmental-impacts-an-australasian-perspective",
          title: 'Marine Renewable Energy: Effectively Balancing the Needs of Developers and Potential Environmental Impacts,...',
          description: "Marine Renewable Energy: Effectively Balancing  the Needs of Developers and  Potential Environmental...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-marine-renewable-energy-effectively-balancing-needs-developers-potential-environmental-impacts-australasian-perspective/";
            },},{id: "library-international-association-for-impact-assessment-annual-conference",
          title: 'International Association for Impact Assessment Annual Conference',
          description: "International Association for Impact Assessment Annual Conference",
          section: "Library",handler: () => {
              window.location.href = "/library/international-association-impact-assessment-annual-conference/";
            },},{id: "library-fair-ideas-sharing-solutions-for-a-sustainable-planet",
          title: 'Fair Ideas: Sharing Solutions for a Sustainable Planet',
          description: "Fair Ideas: Sharing Solutions for a Sustainable Planet",
          section: "Library",handler: () => {
              window.location.href = "/library/fair-ideas-sharing-solutions-sustainable-planet/";
            },},{id: "library-the-anu-rio-20-project-rio-20-lacking-on-energy",
          title: 'The ANU Rio+20 Project: Rio+20 Lacking on Energy',
          description: "The ANU Rio+20 Project: Rio+20 Lacking on Energy",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-anu-rio-20-project-rio-20-lacking-energy/";
            },},{id: "library-the-future-we-definitely-don-t-want",
          title: 'The Future we (Definitely Don’t) Want',
          description: "The Future we (Definitely Don’t) Want",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-future-definitely-dont-want/";
            },},{id: "library-rio-20-crucial-summit-hard-times",
          title: 'Rio+20: crucial summit, hard times',
          description: "Rio+20: crucial summit, hard times",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-rio-20-crucial-summit-hard-times/";
            },},{id: "library-rio-20-the-end-of-the-road",
          title: 'Rio+20, The End of the Road',
          description: "Rio+20, The End of the Road",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-rio-20-end-road/";
            },},{id: "library-marine-renewable-energy-in-australia-the-urgent-need-for-regulatory-reform",
          title: 'Marine Renewable Energy in Australia: the urgent need for regulatory reform',
          description: "Marine Renewable Energy in Australia: the urgent need for regulatory reform",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-marine-renewable-energy-australia-urgent-need-regulatory-reform/";
            },},{id: "library-submission-to-the-australian-competition-and-consumer-commission-certification-trade-mark-application-no-1435347-australian-poultry-industries-association",
          title: 'Submission to the Australian Competition and Consumer Commission: Certification Trade Mark Application No....',
          description: "Submission to the Australian Competition and Consumer Commission: Certification Trade Mark Applicati...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-submission-australian-competition-consumer-commission-certification-trade-mark-application-no-1435347-australian-poultry-industries-association/";
            },},{id: "library-unwired-options-for-increasing-network-demand-management-in-the-national-electricity-market",
          title: 'Unwired: Options for Increasing Network Demand Management in the National Electricity Market',
          description: "Unwired: Options for Increasing Network Demand Management in the National Electricity Market",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-unwired-options-increasing-network-demand-management-national-electricity-market/";
            },},{id: "library-submission-to-the-australian-climate-change-authority-renewable-energy-target-review",
          title: 'Submission to the Australian Climate Change Authority: Renewable Energy Target review',
          description: "Submission to the Australian Climate Change Authority: Renewable Energy Target review",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-submission-australian-climate-change-authority-renewable-energy-target-review/";
            },},{id: "library-submission-to-national-australian-built-environment-rating-system-nabers-administrator-review-of-nabers-ruling-on-proportioning-of-energy-used-by-cogeneration-or-trigeneration-systems",
          title: 'Submission to National Australian Built Environment Rating System (NABERS) Administrator: Review of NABERS...',
          description: "Submission to National Australian Built Environment Rating System (NABERS) Administrator: Review of ...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-submission-national-australian-built-environment-rating-system-nabers-administrator-review-nabers-ruling-proportioning-energy-used-cogeneration-trigeneration-systems/";
            },},{id: "library-submission-to-the-australian-energy-regulator-aer-preliminary-framework-and-approach-ausgrid-endeavour-energy-and-essential-energy-regulatory-control-period-commencing-1-july-2014",
          title: 'Submission to the Australian Energy Regulator (AER): Preliminary Framework and Approach - Ausgrid,...',
          description: "Submission to the Australian Energy Regulator (AER): Preliminary Framework and Approach - Ausgrid, E...",
          section: "Library",handler: () => {
              window.location.href = "/library/submission-australian-energy-regulator-aer-preliminary-framework-approach-ausgrid-endeavour-energy-essential-energy-regulatory-control-period-commencing-1-july-2014/";
            },},{id: "library-wild-law",
          title: 'Wild Law',
          description: "Wild Law",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-wild-law/";
            },},{id: "library-animal-rights-and-the-rights-of-nature-a-brief-overview",
          title: 'Animal Rights and the Rights of Nature, a brief overview',
          description: "Animal Rights and the Rights of Nature, a brief overview",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-animal-rights-rights-nature-brief-overview/";
            },},{id: "library-recent-global-developments-in-marine-renewable-energy",
          title: 'Recent global developments in marine renewable energy',
          description: "Recent global developments in marine renewable energy",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-recent-global-developments-marine-renewable-energy/";
            },},{id: "library-submission-to-the-productivity-commission-electricity-network-regulatory-frameworks",
          title: 'Submission to the Productivity Commission: Electricity Network Regulatory Frameworks',
          description: "Submission to the Productivity Commission: Electricity Network Regulatory Frameworks",
          section: "Library",handler: () => {
              window.location.href = "/library/submission-productivity-commission-electricity-network-regulatory-frameworks/";
            },},{id: "library-environmental-implications-of-increasing-demand-management-in-the-national-electricity-market",
          title: 'Environmental implications of increasing demand management in the National Electricity Market',
          description: "Environmental implications of increasing demand management in the National Electricity Market",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-environmental-implications-increasing-demand-management-national-electricity-market/";
            },},{id: "library-the-future-of-environmental-law-earth-jurisprudence-wild-law-and-the-rights-of-nature",
          title: 'The Future of Environmental Law? Earth Jurisprudence, Wild Law and the Rights of...',
          description: "The Future of Environmental Law? Earth Jurisprudence, Wild Law and the Rights of Nature",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-future-environmental-law-earth-jurisprudence-wild-law-rights-nature/";
            },},{id: "library-animal-law-and-earth-jurisprudence-a-comparative-analysis-of-the-status-of-animals-in-two-emerging-discourses",
          title: 'Animal Law and Earth Jurisprudence: A Comparative Analysis of the Status of Animals...',
          description: "Animal Law and Earth Jurisprudence: A Comparative Analysis of the Status of Animals in two Emerging ...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-animal-law-earth-jurisprudence-comparative-analysis-status-animals-two-emerging-discourses/";
            },},{id: "library-climate-regulation-as-if-the-planet-mattered-the-earth-jurisprudence-approach-to-climate-change",
          title: 'Climate Regulation as if the Planet Mattered: the Earth Jurisprudence Approach to Climate...',
          description: "Climate Regulation as if the Planet Mattered: the Earth Jurisprudence Approach to Climate Change",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-climate-regulation-as-if-planet-mattered-earth-jurisprudence-approach-climate-change/";
            },},{id: "library-ocean-energy-a-legal-perspective",
          title: 'Ocean Energy: A Legal Perspective',
          description: "Ocean Energy: A Legal Perspective",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-ocean-energy-legal-perspective/";
            },},{id: "library-reducing-peak-demand-lowering-prices-but-what-about-emissions",
          title: 'Reducing peak demand: lowering prices, but what about emissions?',
          description: "The past year has seen several processes to reduce the price of electricity to consumers. Each has highlighted the importance of “demand management” - consumers reducing use at peak times to reduce th...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-reducing-peak-demand-lowering-prices-what-emissions/";
            },},{id: "library-reforming-the-national-electricity-objective",
          title: 'Reforming the National Electricity Objective',
          description: "Reforming the National Electricity Objective",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-reforming-national-electricity-objective/";
            },},{id: "library-twitter-for-academics-amp-researchers",
          title: 'Twitter for Academics &amp;amp; Researchers',
          description: "Twitter for Academics &amp; Researchers",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-twitter-academics-researchers/";
            },},{id: "library-virtual-net-metering",
          title: 'Virtual Net Metering',
          description: "Virtual Net Metering",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-virtual-net-metering/";
            },},{id: "library-submission-to-the-australian-energy-market-commission-aemc-review-of-distribution-reliability-outcomes-and-standards",
          title: 'Submission to the Australian Energy Market Commission (AEMC): Review of Distribution Reliability Outcomes...',
          description: "Submission to the Australian Energy Market Commission (AEMC): Review of Distribution Reliability Out...",
          section: "Library",handler: () => {
              window.location.href = "/library/submission-australian-energy-market-commission-aemc-review-distribution-reliability-outcomes-standards/";
            },},{id: "library-submission-to-energy-consumer-advocacy-secretariat-a-national-electricity-consumer-body",
          title: 'Submission to Energy Consumer Advocacy Secretariat: A National Electricity Consumer Body',
          description: "Submission to Energy Consumer Advocacy Secretariat: A National Electricity Consumer Body",
          section: "Library",handler: () => {
              window.location.href = "/library/submission-energy-consumer-advocacy-secretariat-national-electricity-consumer-body/";
            },},{id: "library-submission-to-new-south-wales-government-nsw-smart-meter-task-force",
          title: 'Submission to New South Wales Government: NSW Smart Meter Task Force',
          description: "Submission to New South Wales Government: NSW Smart Meter Task Force",
          section: "Library",handler: () => {
              window.location.href = "/library/submission-new-south-wales-government-nsw-smart-meter-task-force/";
            },},{id: "library-submission-to-queensland-government-department-of-energy-and-water-supply-30-year-electricity-strategy",
          title: 'Submission to Queensland Government Department of Energy and Water Supply: 30-Year Electricity Strategy...',
          description: "Submission to Queensland Government Department of Energy and Water Supply: 30-Year Electricity Strat...",
          section: "Library",handler: () => {
              window.location.href = "/library/submission-queensland-government-department-energy-water-supply-30-year-electricity-strategy/";
            },},{id: "library-reducing-peak-demand-targets-are-good-practice",
          title: 'Reducing peak demand: targets are good practice',
          description: "Better managing peak demand, the primary culprit behind recent rapid price rises across Australia, is a key challenge facing Eastern Australia’s National Electricity Market (NEM). To deal with peak de...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-reducing-peak-demand-targets-good-practice/";
            },},{id: "library-submission-to-the-australian-energy-regulator-aer-regulatory-investment-test-distribution",
          title: 'Submission to the Australian Energy Regulator (AER): Regulatory Investment Test - Distribution',
          description: "Submission to the Australian Energy Regulator (AER): Regulatory Investment Test - Distribution",
          section: "Library",handler: () => {
              window.location.href = "/library/submission-australian-energy-regulator-aer-regulatory-investment-test-distribution/";
            },},{id: "library-tackling-peak-power-demands",
          title: 'Tackling peak power demands',
          description: "Tackling peak power demands",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-tackling-peak-power-demands/";
            },},{id: "library-control-mechanisms-for-new-south-wales-nsw-distribitution-network-service-providers-dnsps-2014-2019",
          title: 'Control Mechanisms for New South Wales (NSW) Distribitution Network Service Providers (DNSPs), 2014-2019...',
          description: "Control Mechanisms for New South Wales (NSW) Distribitution Network Service Providers (DNSPs), 2014-...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-control-mechanisms-new-south-wales-nsw-distribitution-network-service-providers-dnsps-2014-2019/";
            },},{id: "library-submission-to-the-department-of-resources-energy-amp-tourism-energy-efficiency-opportunities-program-new-developments-regulations",
          title: 'Submission to the Department of Resources, Energy &amp;amp; Tourism: Energy Efficiency Opportunities Program...',
          description: "Submission to the Department of Resources, Energy &amp; Tourism: Energy Efficiency Opportunities Program...",
          section: "Library",handler: () => {
              window.location.href = "/library/submission-department-resources-energy-tourism-energy-efficiency-opportunities-program-new-developments-regulations/";
            },},{id: "library-book-review-animal-harm-perspectives-on-why-people-harm-and-kill-animals",
          title: 'Book Review: Animal Harm: Perspectives on Why People Harm and Kill Animals',
          description: "Book Review: Animal Harm: Perspectives on Why People Harm and Kill Animals",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-book-review-animal-harm-perspectives-why-people-harm-kill-animals/";
            },},{id: "library-sumbission-to-the-australian-energy-market-commission-aemc-strategic-priorities",
          title: 'Sumbission to the Australian Energy Market Commission (AEMC): Strategic priorities',
          description: "Sumbission to the Australian Energy Market Commission (AEMC): Strategic priorities",
          section: "Library",handler: () => {
              window.location.href = "/library/sumbission-australian-energy-market-commission-aemc-strategic-priorities/";
            },},{id: "library-submission-to-the-australian-energy-market-commission-aemc-draft-regulatory-investment-test-for-disctribution-and-application-guidelines-rit-d",
          title: 'Submission to the Australian Energy Market Commission (AEMC): Draft regulatory investment test for...',
          description: "Submission to the Australian Energy Market Commission (AEMC): Draft regulatory investment test for d...",
          section: "Library",handler: () => {
              window.location.href = "/library/submission-australian-energy-market-commission-aemc-draft-regulatory-investment-test-disctribution-application-guidelines-rit-d/";
            },},{id: "library-visiting-fellowship-international-centre-for-island-technology",
          title: 'Visiting Fellowship: International Centre for Island Technology',
          description: "Visiting Fellowship: International Centre for Island Technology",
          section: "Library",handler: () => {
              window.location.href = "/library/visiting-fellowship-international-centre-island-technology/";
            },},{id: "library-advancing-marine-biodiversity-protection-through-regional-fisheries-management-a-review-of-high-seas-bottom-fisheries-closures",
          title: 'Advancing marine biodiversity protection through regional fisheries management: a review of high seas...',
          description: "Ocean regions that do not fall under the jurisdiction of any State, areas beyond national jurisdiction (ABNJ or the “high seas”),1 represent almost half of the planet’s surface and a significant porti...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-advancing-marine-biodiversity-protection-regional-fisheries-management-review-high-seas-bottom-fisheries-closures/";
            },},{id: "library-the-scores-at-half-time-an-update-on-the-international-discussions-on-the-governance-of-marine-biodiversity-in-areas-beyond-national-jurisdiction",
          title: 'The Scores at Half Time: An update on the international discussions on the...',
          description: "Marine areas beyond national jurisdiction (ABNJ) represent around half of the Planet’s surface and a significant amount of its biodiversity. Over the past decades, the international community has beco...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-scores-half-time-update-international-discussions-governance-marine-biodiversity-areas-beyond-national-jurisdiction/";
            },},{id: "library-marine-governance-in-an-industrialised-ocean-a-marine-renewable-energy-case-study-poster",
          title: 'Marine Governance in an Industrialised Ocean A Marine Renewable Energy case study (poster)...',
          description: "Marine Governance in an Industrialised Ocean A Marine Renewable Energy case study (poster)",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-marine-governance-industrialised-ocean-marine-renewable-energy-case-poster/";
            },},{id: "library-regulating-marine-renewable-energy-development-a-preliminary-assessment-of-uk-permitting-processes",
          title: 'Regulating marine renewable energy development: a preliminary assessment of UK permitting processes',
          description: "Regulating marine renewable energy development: a preliminary assessment of UK permitting processes",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-regulating-marine-renewable-energy-development-preliminary-assessment-uk-permitting-processes/";
            },},{id: "library-governing-the-high-seas-linking-global-governance-and-regional-implementation",
          title: 'Governing the “High Seas” - Linking global governance and regional implementation',
          description: "Marine areas beyond national jurisdiction (ABJN), often referred to as the “High Seas1”, represent around half of the Planet’s surface and host a significant portion of its biodiversity. Despite their...",
          section: "Library",handler: () => {
              window.location.href = "/library/governing-high-seas-linking-global-governance-regional-implementation/";
            },},{id: "library-renewables-2014-global-status-report",
          title: 'Renewables 2014 Global Status Report',
          description: "Renewables 2014 Global Status Report",
          section: "Library",handler: () => {
              window.location.href = "/library/renewables-2014-global-status-report/";
            },},{id: "library-marine-spatial-planning-in-areas-beyond-national-jurisdiction-developing-a-research-agenda",
          title: 'Marine Spatial Planning in Areas Beyond National Jurisdiction: developing a research agenda',
          description: "Marine Spatial Planning in Areas Beyond National Jurisdiction: developing a research agenda",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-marine-spatial-planning-areas-beyond-national-jurisdiction-developing-research-agenda/";
            },},{id: "library-sumbission-to-department-of-industry-energy-white-paper",
          title: 'Sumbission to Department of Industry: Energy White Paper',
          description: "Sumbission to Department of Industry: Energy White Paper",
          section: "Library",handler: () => {
              window.location.href = "/library/sumbission-department-industry-energy-white/";
            },},{id: "library-reforming-and-harmonising-the-nsw-energy-savings-scheme",
          title: 'Reforming and Harmonising the NSW Energy Savings Scheme',
          description: "Reforming and Harmonising the NSW Energy Savings Scheme",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-reforming-harmonising-nsw-energy-savings-scheme/";
            },},{id: "library-eighth-meeting-of-the-ad-hoc-open-ended-informal-working-group-to-study-issues-relating-to-the-conservation-and-sustainable-use-of-marine-biological-diversity-beyond-areas-of-national-jurisdiction",
          title: 'Eighth meeting of the Ad Hoc Open-ended Informal Working Group to study issues...',
          description: "Eighth meeting of the Ad Hoc Open-ended Informal Working Group to study issues relating to the conse...",
          section: "Library",handler: () => {
              window.location.href = "/library/eighth-meeting-ad-hoc-open-ended-informal-working-group-issues-relating-conservation-sustainable-use-marine-biological-diversity-beyond-areas-national-jurisdiction/";
            },},{id: "library-la-gobernanza-de-las-zonas-fuera-de-la-jurisdicción-nacional",
          title: 'La Gobernanza de las zonas fuera de la jurisdicción nacional',
          description: "La Gobernanza de las zonas fuera de la jurisdicción nacional",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-la-gobernanza-de-las-zonas-fuera-de-la-jurisdiccion-nacional/";
            },},{id: "library-marine-governance-in-an-industrialised-ocean-a-case-study-of-the-uk-39-s-emerging-marine-renewable-energy-industry",
          title: 'Marine Governance in an Industrialised Ocean: a case study of the UK&amp;#39;s emerging...',
          description: "Marine Governance in an Industrialised Ocean: a case study of the UK&#39;s emerging marine renewable ene...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-marine-governance-industrialised-ocean-case-uks-emerging-marine-renewable-energy-industry/";
            },},{id: "library-sustainably-advancing-the-blue-economy-environmental-impact-assessment-of-of-marine-renewable-energy-projects-in-the-uk",
          title: 'Sustainably advancing the Blue Economy: Environmental Impact Assessment of of Marine Renewable Energy...',
          description: "Sustainably advancing the Blue Economy: Environmental Impact Assessment of of Marine Renewable Energ...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-sustainably-advancing-blue-economy-environmental-impact-assessment-marine-renewable-energy-projects-uk/";
            },},{id: "library-halloween-special-spooky-research-from-the-cold-depths-of-academia",
          title: 'Halloween special: spooky research from the cold depths of academia',
          description: "Could vampires exist (mathematically speaking)? What causes ghostly cold chills? And what does death smell like? Researcher Glen Wright investigates",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-halloween-special-spooky-research-cold-depths-academia/";
            },},{id: "library-how-to-make-a-cup-of-tea-for-an-academic",
          title: 'How to make a cup of tea for an academic',
          description: "Ever wondered where all the bloody teaspoons are? Or how to avoid that pesky dribble down the underside of the teapot spout? Thankfully researchers have tackled these pressing issues",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-how-make-cup-tea-academic/";
            },},{id: "library-proof-that-academia-is-teeming-with-humour-wit-and-general-oddness",
          title: 'Proof that academia is teeming with humour, wit… and general oddness',
          description: "In a new fortnightly series, researcher Glen Wright attempts to prove academia is not entirely full of stuffiness by sharing some amusing oddities",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-proof-academia-teeming-humour-wit-general-oddness/";
            },},{id: "library-strengthening-the-role-of-science-in-marine-governance-through-environmental-impact-assessment-a-case-study-of-the-marine-renewable-energy-industry",
          title: 'Strengthening the role of science in marine governance through environmental impact assessment: a...',
          description: "Strengthening the role of science in marine governance through environmental impact assessment: a ca...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-strengthening-role-science-marine-governance-environmental-impact-assessment-case-marine-renewable-energy-industry/";
            },},{id: "library-potsdam-ocean-governance-workshop-entry-points-to-sustainability",
          title: 'Potsdam Ocean Governance Workshop: Entry Points to Sustainability',
          description: "Potsdam Ocean Governance Workshop: Entry Points to Sustainability",
          section: "Library",handler: () => {
              window.location.href = "/library/potsdam-ocean-governance-workshop-entry-points-sustainability/";
            },},{id: "library-academia-and-food-stale-snacks-and-strange-research",
          title: 'Academia and food: stale snacks and strange research',
          description: "Are you a PhD student surviving on left-over crisps? Studies show that sound effects alone can help freshen up old food",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-academia-food-stale-snacks-strange-research/";
            },},{id: "library-rights-and-ownership-in-marine-spaces",
          title: 'Rights and Ownership in Marine Spaces',
          description: "Rights and Ownership in Marine Spaces",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-rights-ownership-marine-spaces/";
            },},{id: "library-towards-a-new-international-agreement-on-high-seas-biodiversity",
          title: 'Towards a New International Agreement on High Seas Biodiversity',
          description: "Towards a New International Agreement on High Seas Biodiversity",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-towards-new-international-agreement-high-seas-biodiversity/";
            },},{id: "library-towards-a-new-international-instrument-on-the-conservation-and-sustainable-use-of-marine-biodiversity-in-areas-beyond-national-jurisdiction",
          title: 'Towards a new international instrument on the conservation and sustainable use of marine...',
          description: "Towards a new international instrument on the  conservation and sustainable use of marine  biodivers...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-towards-new-international-instrument-conservation-sustainable-use-marine-biodiversity-areas-beyond-national-jurisdiction/";
            },},{id: "library-world-parks-congress",
          title: 'World Parks Congress',
          description: "World Parks Congress",
          section: "Library",handler: () => {
              window.location.href = "/library/world-parks-congress/";
            },},{id: "library-will-climate-change-kill-santa-claus-this-and-more-festive-themed-research",
          title: 'Will climate change kill Santa Claus? This and more festive-themed research',
          description: "From diagnosing Rudolph’s red nose to festive spices that make you happy, Glen Wright picks out some of the best Christmassy research",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-climate-change-kill-santa-claus-festive-themed-research/";
            },},{id: "library-a-guide-to-the-ref-for-the-shameless-academic",
          title: 'A guide to the REF for the shameless academic',
          description: "Palm your teaching off on gullible colleagues and get yourself a TV show – Glen Wright shares his tips for success in the Research Excellence Framework",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-guide-ref-shameless-academic/";
            },},{id: "library-towards-a-new-international-instrument-on-the-conservation-and-sustainable-use-of-marine-biodiversity-in-abnj",
          title: 'Towards a new international instrument on the conservation and sustainable use of marine...',
          description: "Towards a new international instrument on the  conservation and sustainable use of marine  biodivers...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-towards-new-international-instrument-conservation-sustainable-use-marine-biodiversity-abnj/";
            },},{id: "library-advancing-governance-of-marine-areas-beyond-national-jurisdiction",
          title: 'Advancing governance of marine areas beyond national jurisdiction',
          description: "Advancing governance of marine areas beyond national jurisdiction",
          section: "Library",handler: () => {
              window.location.href = "/library/advancing-governance-marine-areas-beyond-national-jurisdiction/";
            },},{id: "library-accommodating-ocean-energy-in-marine-spatial-planning-processes",
          title: 'Accommodating Ocean Energy in Marine Spatial Planning Processes',
          description: "Accommodating Ocean Energy in Marine Spatial Planning Processes",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-accommodating-ocean-energy-marine-spatial-planning-processes/";
            },},{id: "library-advancing-marine-biodiversity-protection-through-regional-fisheries-management-a-review-of-bottom-fisheries-closures-in-areas-beyond-national-jurisdiction",
          title: 'Advancing marine biodiversity protection through regional fisheries management: A review of bottom fisheries...',
          description: "Fishing is a significant threat to marine biodiversity in areas beyond national jurisdiction (ABNJ). Bottom fishing in particular can impact deep-sea ecosystems, and the UN General Assembly has called...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-advancing-marine-biodiversity-protection-regional-fisheries-management-review-bottom-fisheries-closures-areas-beyond-national-jurisdiction/";
            },},{id: "library-developing-area-based-management-tools-in-areas-beyond-national-jurisdiction-possible-options-for-the-western-indian-ocean",
          title: 'Developing area-based management tools in areas beyond national jurisdiction: possible options for the...',
          description: "Developing area-based management tools in areas beyond national jurisdiction: possible options for t...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-developing-area-based-management-tools-areas-beyond-national-jurisdiction-possible-options-western-indian-ocean/";
            },},{id: "library-this-study-is-intentionally-left-blank",
          title: 'This Study is Intentionally Left Blank',
          description: "This Study is Intentionally Left Blank",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-intentionally-left-blank/";
            },},{id: "library-marine-protected-areas-in-areas-beyond-national-jurisdiction",
          title: 'Marine protected areas in areas beyond national jurisdiction',
          description: "Marine protected areas in areas beyond national jurisdiction",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-marine-protected-areas-areas-beyond-national-jurisdiction/";
            },},{id: "library-ocean-energy-key-legal-issues-and-challenges",
          title: 'Ocean energy: key legal issues and challenges',
          description: "Ocean energy: key legal issues and challenges",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-ocean-energy-key-legal-issues-challenges/";
            },},{id: "library-marine-governance-in-an-industrialised-ocean-a-case-study-of-the-emerging-marine-renewable-energy-industry",
          title: 'Marine governance in an industrialised ocean: A case study of the emerging marine...',
          description: "The world&#39;s oceans are currently undergoing an unprecedented period of industrialisation, made possible by advances in technology and driven by our growing need for food, energy and resources. This is...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-marine-governance-industrialised-ocean-case-emerging-marine-renewable-energy-industry/";
            },},{id: "library-marine-renewable-energy-community-consultation-and-planning-summary-of-the-international-network-for-social-studies-of-marine-energy-issmer-online-seminar-series-november-2014-january-2015",
          title: 'Marine Renewable Energy: Community, Consultation and Planning (Summary of the International network for...',
          description: "The MRE industry is at a crucial moment. Devices are now moving from engineering drawings to full-scale prototypes, and the first commercial scale wave and tide energy farms have been announced and ar...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-marine-renewable-energy-community-consultation-planning-summary-international-network-social-studies-marine-energy-issmer-online-seminar-series-november-2014-january-2015/";
            },},{id: "library-a-new-chapter-for-the-high-seas-historic-decision-to-negotiate-an-international-legally-binding-instrument-on-the-conservation-and-sustainable-use-of-marine-biodiversity-in-areas-beyond-national-jurisdiction",
          title: 'A new chapter for the high seas? Historic decision to negotiate an international...',
          description: "Marine areas beyond national jurisdiction (ABNJ) represent around half of the Planet’s surface and a significant amount of its biodiversity. In recent years, the international community has become inc...",
          section: "Library",handler: () => {
              window.location.href = "/library/new-chapter-high-seas-historic-decision-negotiate-international-legally-binding-instrument-conservation-sustainable-use-marine-biodiversity-areas-beyond-national-jurisdiction/";
            },},{id: "library-ninth-meeting-of-the-ad-hoc-open-ended-informal-working-group-to-study-issues-relating-to-the-conservation-and-sustainable-use-of-marine-biological-diversity-beyond-areas-of-national-jurisdiction",
          title: 'Ninth meeting of the Ad Hoc Open-ended Informal Working Group to study issues...',
          description: "Ninth meeting of the Ad Hoc Open-ended Informal Working Group to study issues relating to the conser...",
          section: "Library",handler: () => {
              window.location.href = "/library/ninth-meeting-ad-hoc-open-ended-informal-working-group-issues-relating-conservation-sustainable-use-marine-biological-diversity-beyond-areas-national-jurisdiction/";
            },},{id: "library-strengthening-the-international-regulation-of-offshore-oil-and-gas-activities",
          title: 'Strengthening the international regulation of offshore oil and gas activities',
          description: "Strengthening the international regulation of offshore oil and gas activities",
          section: "Library",handler: () => {
              window.location.href = "/library/strengthening-international-regulation-offshore-oil-gas-activities/";
            },},{id: "library-dreading-valentine-39-s-here-39-s-a-rigorously-academic-research-backed-guide-to-love",
          title: 'Dreading Valentine&amp;#39;s? Here&amp;#39;s a rigorously academic, research-backed guide to love',
          description: "Love is no simple matter. Fortunately, there’s plenty of academic research to help you find – and satisfy – your soulmate",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-dreading-valentines-heres-rigorously-academic-research-backed-guide-love/";
            },},{id: "library-regional-approaches-for-abnj-state-of-play",
          title: 'Regional approaches for ABNJ – state of play',
          description: "Regional approaches for ABNJ – state of play",
          section: "Library",handler: () => {
              window.location.href = "/library/regional-approaches-abnj-state-play/";
            },},{id: "library-rights-and-ownership-in-sea-country-implications-of-marine-renewable-energy-for-indigenous-and-local-communities",
          title: 'Rights and ownership in sea country: implications of marine renewable energy for indigenous...',
          description: "The adoption of UN Convention of the Law of the Sea in 1982 created optimism for indigenous peoples and marginalised coastal communities that they may (re)gain control of, or improve access to, marine...",
          section: "Library",handler: () => {
              window.location.href = "/library/rights-ownership-sea-country-implications-marine-renewable-energy-indigenous-local-communities/";
            },},{id: "library-workshop-on-linking-global-and-regional-levels-in-the-management-of-marine-areas-beyond-national-jurisdiction",
          title: 'Workshop on Linking Global and Regional Levels in the Management of Marine Areas...',
          description: "Workshop on Linking Global and Regional Levels in the Management of Marine Areas Beyond National Jur...",
          section: "Library",handler: () => {
              window.location.href = "/library/workshop-linking-global-regional-levels-management-marine-areas-beyond-national-jurisdiction/";
            },},{id: "library-top-five-university-pranks-to-watch-out-for-on-april-fools-39-day",
          title: 'Top five university pranks to watch out for on April Fools&amp;#39; day',
          description: "Hoisted cars, fake students and remodeled buildings – practical jokes have a long history on university campuses. Here are some of the most notorious",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-top-five-university-pranks-watch-april-fools-day/";
            },},{id: "library-dealing-with-the-risk-of-licensing-marine-renewables-the-role-and-experience-of-regulators",
          title: 'Dealing with the risk of licensing marine renewables: The role and experience of...',
          description: "The RiCORE project aims at designing ways to accelerate and streamline the environmental requirements associated with consents for novel marine renewable technologies, including offshore wind, wave an...",
          section: "Library",handler: () => {
              window.location.href = "/library/dealing-risk-licensing-marine-renewables-role-experience-regulators/";
            },},{id: "library-researcher-glen-wright-to-take-over-wiley-s-exchanges-blog",
          title: 'Researcher Glen Wright to take over Wiley’s Exchanges Blog',
          description: "Hoboken, NJ – May 7, 2015 – John Wiley &amp; Sons, Inc., is pleased to welcome Glen Wright, a research fellow at the Institute for Sustainable Development and International Relations (IDDRI) in Paris, as ...",
          section: "Library",handler: () => {
              window.location.href = "/library/researcher-glen-wright-take-wileys-exchanges-blog/";
            },},{id: "library-towards-a-european-research-agenda-for-ocean-governance-an-expert-workshop",
          title: 'Towards a European Research Agenda for Ocean Governance: An Expert Workshop',
          description: "Towards a European Research Agenda for Ocean Governance: An Expert Workshop",
          section: "Library",handler: () => {
              window.location.href = "/library/towards-european-research-agenda-ocean-governance-expert-workshop/";
            },},{id: "library-scoping-workshop-supporting-the-development-of-regional-initiatives-for-abnj-in-the-abidjan-convention-region",
          title: 'Scoping Workshop: Supporting the development of regional initiatives for ABNJ in the Abidjan...',
          description: "1. The Convention for Cooperation in the Protection, Management and Development of the Marine and Coastal Environment of the Atlantic Coast of the West, Central and Southern Africa Region (Abidjan Con...",
          section: "Library",handler: () => {
              window.location.href = "/library/scoping-workshop-supporting-development-regional-initiatives-abnj-abidjan-convention-region/";
            },},{id: "library-what-role-for-the-nairobi-convention-in-the-high-seas",
          title: 'What role for the Nairobi Convention in the high seas?',
          description: "What role for the Nairobi Convention in the high seas?",
          section: "Library",handler: () => {
              window.location.href = "/library/what-role-nairobi-convention-high-seas/";
            },},{id: "library-collation-of-building-blocks-and-different-options-for-an-unclos-implementing-agreement",
          title: 'Collation of Building Blocks and Different Options for an UNCLOS Implementing Agreement',
          description: "Collation of Building Blocks and Different Options for an UNCLOS Implementing Agreement",
          section: "Library",handler: () => {
              window.location.href = "/library/collation-building-blocks-different-options-unclos-implementing-agreement/";
            },},{id: "library-bottom-fisheries-closures-in-areas-beyond-national-jurisdiction",
          title: 'Bottom Fisheries Closures in Areas Beyond National Jurisdiction',
          description: "Bottom Fisheries Closures in Areas Beyond National Jurisdiction",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-bottom-fisheries-closures-areas-beyond-national-jurisdiction/";
            },},{id: "library-la-haute-mer-historique-et-perspectives",
          title: 'La Haute Mer: Historique et perspectives',
          description: "La Haute Mer: Historique et perspectives",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-la-haute-mer-historique-et-perspectives/";
            },},{id: "library-regional-ocean-governance-conservation-and-sustainable-use-of-marine-biodiversity",
          title: 'Regional Ocean Governance  Conservation and Sustainable Use of Marine Biodiversity',
          description: "Regional Ocean Governance  Conservation and Sustainable Use of Marine Biodiversity",
          section: "Library",handler: () => {
              window.location.href = "/library/regional-ocean-governance-conservation-sustainable-use-marine-biodiversity/";
            },},{id: "library-implementing-the-ocean-sdg-from-knowledge-to-action",
          title: 'Implementing the Ocean SDG: from knowledge to action',
          description: "Implementing the Ocean SDG: from knowledge to action",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-implementing-ocean-sdg-knowledge-action/";
            },},{id: "library-the-northwest-passage-legal-status-and-issues",
          title: 'The Northwest Passage: Legal status and issues',
          description: "The Northwest Passage: Legal status and issues",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-northwest-passage-legal-status-issues/";
            },},{id: "library-an-international-instrument-on-conservation-and-sustainable-use-of-biodiversity-in-marine-areas-beyond-national-jurisdiction-matrix-of-suggestions",
          title: 'An International Instrument on Conservation and Sustainable Use of Biodiversity in Marine Areas...',
          description: "An International Instrument on Conservation and Sustainable Use of Biodiversity in Marine Areas beyo...",
          section: "Library",handler: () => {
              window.location.href = "/library/international-instrument-conservation-sustainable-use-biodiversity-marine-areas-beyond-national-jurisdiction-matrix-suggestions/";
            },},{id: "library-academics-with-cats-2016-the-winning-photographs",
          title: 'Academics With Cats 2016: the winning photographs',
          description: "Academics With Cats 2016: the winning photographs",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-academics-cats-2016-winning-photographs/";
            },},{id: "library-environmental-impact-assessment-to-support-marine-innovation-the-rochdale-envelope-and-deploy-amp-monitor-in-the-uk-39-s-ocean-energy-industry",
          title: 'Environmental Impact Assessment to Support Marine Innovation: The ‘Rochdale Envelope’ and ‘Deploy &amp;amp;...',
          description: "A new industrial revolution is taking place in the oceans, as humankind increasing looks offshore to meet its needs for energy, resources and food. This growing demand for marine space and resources i...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-environmental-impact-assessment-support-marine-innovation-rochdale-envelope-deploy-monitor-uks-ocean-energy-industry/";
            },},{id: "library-establishing-a-legal-research-agenda-for-ocean-energy",
          title: 'Establishing a legal research agenda for ocean energy',
          description: "The literature on ocean energy has, to date, largely focussed on technical, environmental, and, increasingly, social and political aspects. Legal and regulatory factors have received far less attentio...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-establishing-legal-research-agenda-ocean-energy/";
            },},{id: "library-high-seas-fisheries-what-role-for-a-new-international-instrument",
          title: 'High seas fisheries: what role for a new international instrument?',
          description: "States are currently discussing the development of a new international legally binding instrument (ILBI) on the conservation and sustainable use of marine biological diversity of areas beyond national...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-high-seas-fisheries-what-role-new-international-instrument/";
            },},{id: "library-the-long-and-winding-road-continues-towards-a-new-agreement-on-high-seas-governance",
          title: 'The long and winding road continues: Towards a new agreement on high seas...',
          description: "In 2015, States agreed to launch negotiations for the elaboration of an international legally binding instrument dedicated to the conservation and sustainable use of the marine biological diversity of...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-long-winding-road-continues-towards-new-agreement-high-seas-governance/";
            },},{id: "library-an-overview-of-vulnerable-marine-ecosystem-closures",
          title: 'An overview of vulnerable marine ecosystem closures',
          description: "An overview of vulnerable marine ecosystem closures",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-overview-vulnerable-marine-ecosystem-closures/";
            },},{id: "library-sea-change-negotiating-a-new-agreement-on-the-conservation-and-sustainable-use-of-marine-biodiversity-in-areas-beyond-national-jurisdiction",
          title: 'Sea change: Negotiating a new agreement on the conservation and sustainable use of...',
          description: "Sea change: Negotiating a new agreement on the conservation and sustainable use of marine biodiversi...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-sea-change-negotiating-new-agreement-conservation-sustainable-use-marine-biodiversity-areas-beyond-national-jurisdiction/";
            },},{id: "library-sustainable-development-of-the-oceans-closing-the-gaps-in-the-international-legal-framework",
          title: 'Sustainable development of the oceans: Closing the gaps in the international legal framework...',
          description: "The world’s oceans are critical providers of ecosystem services and they are under increasing pressure from expanding and intensifying human activities. A range of international instruments and instit...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-sustainable-development-oceans-closing-gaps-international-legal-framework/";
            },},{id: "library-regulating-wave-and-tidal-energy-an-industry-perspective-on-the-scottish-marine-governance-framework",
          title: 'Regulating wave and tidal energy: An industry perspective on the Scottish marine governance...',
          description: "Regulating wave and tidal energy: An industry perspective on the Scottish marine governance framewor...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-regulating-wave-tidal-energy-industry-perspective-scottish-marine-governance-framework/";
            },},{id: "library-protecting-earth-39-s-last-conservation-frontier-scientific-management-and-legal-priorities-for-mpas-beyond-national-boundaries",
          title: 'Protecting Earth&amp;#39;s last conservation frontier: scientific, management and legal priorities for MPAs beyond...',
          description: "1. Marine areas beyond national jurisdiction (ABNJ) comprise most of Earth&#39;s interconnected ocean, hosting complex ecosystems that play key roles in sustaining life and providing important goods and s...",
          section: "Library",handler: () => {
              window.location.href = "/library/protecting-earths-last-conservation-frontier-scientific-management-legal-priorities-mpas-beyond-national-boundaries/";
            },},{id: "library-conservation-and-sustainable-use-of-marine-biological-diversity-of-areas-beyond-national-jurisdiction-preparing-for-the-prepcom",
          title: 'Conservation and Sustainable Use of Marine Biological Diversity of Areas Beyond National Jurisdiction:...',
          description: "Conservation and Sustainable Use of Marine Biological Diversity of Areas Beyond National Jurisdictio...",
          section: "Library",handler: () => {
              window.location.href = "/library/conservation-sustainable-use-marine-biological-diversity-areas-beyond-national-jurisdiction-preparing-prepcom/";
            },},{id: "library-environmental-impact-assessment-developing-options-for-abnj",
          title: 'Environmental Impact Assessment: Developing options for ABNJ',
          description: "Environmental Impact Assessment: Developing options for ABNJ",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-environmental-impact-assessment-developing-options-abnj/";
            },},{id: "library-atelier-littocean-pour-des-espaces-maritimes-équitables-les-énergies-marines-renouvelables-illusion-ou-réalité",
          title: 'Atelier LittOcean: Pour des espaces maritimes équitables : les énergies marines renouvelables, illusion...',
          description: "Atelier LittOcean: Pour des espaces maritimes équitables : les énergies marines renouvelables, illus...",
          section: "Library",handler: () => {
              window.location.href = "/library/atelier-littocean-pour-des-espaces-maritimes-equitables-les-energies-marines-renouvelables-illusion-ou-realite/";
            },},{id: "library-tout-comprendre-des-prochaines-négociations-sur-la-gouvernance-de-la-haute-mer",
          title: 'Tout comprendre des prochaines négociations sur la gouvernance de la haute mer',
          description: "Tout comprendre des prochaines négociations sur la gouvernance de la haute mer",
          section: "Library",handler: () => {
              window.location.href = "/library/tout-comprendre-des-prochaines-negociations-sur-la-gouvernance-de-la-haute-mer/";
            },},{id: "library-training-programme-on-the-sustainable-development-and-governance-of-the-caspian-sea",
          title: 'Training Programme on the Sustainable Development and Governance of the Caspian Sea',
          description: "Training Programme on the Sustainable Development and Governance of the Caspian Sea",
          section: "Library",handler: () => {
              window.location.href = "/library/training-programme-sustainable-development-governance-caspian-sea/";
            },},{id: "library-un-high-seas-treaty-negotiations",
          title: 'UN High Seas treaty negotiations',
          description: "UN High Seas treaty negotiations",
          section: "Library",handler: () => {
              window.location.href = "/library/un-high-seas-treaty-negotiations/";
            },},{id: "library-un-rendez-vous-historique-pour-protéger-la-haute-mer-des-convoitises",
          title: 'Un rendez-vous historique pour protéger la haute mer des convoitises',
          description: "Un rendez-vous historique pour protéger la haute mer des convoitises",
          section: "Library",handler: () => {
              window.location.href = "/library/un-rendez-vous-historique-pour-proteger-la-haute-mer-des-convoitises/";
            },},{id: "library-first-session-of-the-preparatory-committee-established-by-the-un-general-assembly-resolution-69-292-development-of-an-international-legally-binding-instrument-under-the-united-nations-convention-on-the-law-of-the-sea-on-the-conservation-and-sustainable-use-of-marine-biological-diversity-of-areas-beyond-national-jurisdiction",
          title: 'First Session of the Preparatory Committee Established by the UN General Assembly Resolution...',
          description: "First Session of the Preparatory Committee Established by the UN General Assembly Resolution 69/292 ...",
          section: "Library",handler: () => {
              window.location.href = "/library/first-session-preparatory-committee-established-un-general-assembly-resolution-69-292-development-international-legally-binding-instrument-united-nations-convention-law-sea-conservation-sustainable/";
            },},{id: "library-vers-un-accord-sur-la-haute-mer-des-mesures-positives-à-new-york",
          title: 'Vers un accord sur la haute mer : des mesures positives à New...',
          description: "Alors que nous sommes à un moment décisif pour l&#39;avenir de l&#39;océan, plus de 80 États se sont réunis au siège de l&#39;ONU à New York (30 Mars - 8 Avril) pour lancer les négociations d&#39;un nouvel accord sur...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-vers-un-accord-sur-la-haute-mer-des-mesures-positives-a-new-york/";
            },},{id: "library-l-union-européenne-va-t-elle-enfin-mettre-un-terme-au-chalutage-profond",
          title: 'L’Union européenne va-t-elle enfin mettre un terme au chalutage profond ?',
          description: "Désastreuse pour les écosystèmes marins, la pêche en eaux profondes fait l’objet de vifs débats à Bruxelles. Une nouvelle réglementation européenne encadrant cette pratique est attendue à l’été 2016.",
          section: "Library",handler: () => {
              window.location.href = "/library/lunion-europeenne-va-t-elle-enfin-mettre-un-terme-au-chalutage-profond/";
            },},{id: "library-talks-aim-to-tame-marine-wild-west-nations-debate-how-to-protect-biodiversity-in-the-high-seas",
          title: 'Talks aim to tame marine Wild West: Nations debate how to protect biodiversity...',
          description: "Talks aim to tame marine Wild West: Nations debate how to protect biodiversity in the high seas",
          section: "Library",handler: () => {
              window.location.href = "/library/talks-aim-tame-marine-wild-west-nations-debate-how-protect-biodiversity-high-seas/";
            },},{id: "library-interdiction-du-chalutage-profond-une-belle-victoire-et-quelques-concessions",
          title: 'Interdiction du chalutage profond : une belle victoire et quelques concessions',
          description: "Le 30 juin dernier, l’Union européenne décidait après des années d’âpres négociations d’interdire la pêche en eau profonde au-delà de 800 mètres. Retour sur cet accord historique.",
          section: "Library",handler: () => {
              window.location.href = "/library/interdiction-du-chalutage-profond-une-belle-victoire-et-quelques-concessions/";
            },},{id: "library-historic-un-talks-could-save-the-high-seas",
          title: 'Historic UN talks could save the high seas',
          description: "Since the adoption of the United Nations (UN) Convention on the Law of the Sea (UNCLOS) in 1982, human activities in areas beyond national jurisdiction (ABNJ)1 have developed exponentially. Existing a...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-historic-un-talks-save-high-seas/";
            },},{id: "library-cautious-steps-towards-a-new-high-seas-agreement",
          title: 'Cautious steps towards a new high seas agreement',
          description: "Seeking to fill the gaps in the international legal framework for ocean governance, States gathered at the UN headquarters in New York (26 August-9 September) to discuss elements of an agreement on th...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-cautious-steps-towards-new-high-seas-agreement/";
            },},{id: "library-environmental-impact-assessment-and-overarching-provisions",
          title: 'Environmental Impact Assessment and Overarching Provisions',
          description: "Environmental Impact Assessment and Overarching Provisions",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-environmental-impact-assessment-overarching-provisions/";
            },},{id: "library-second-session-of-the-preparatory-committee-established-by-the-un-general-assembly-resolution-69-292-development-of-an-international-legally-binding-instrument-under-the-united-nations-convention-on-the-law-of-the-sea-on-the-conservation-and-sustainable-use-of-marine-biological-diversity-of-areas-beyond-national-jurisdiction",
          title: 'Second Session of the Preparatory Committee Established by the UN General Assembly Resolution...',
          description: "Second Session of the Preparatory Committee Established by the UN General Assembly Resolution 69/292...",
          section: "Library",handler: () => {
              window.location.href = "/library/second-session-preparatory-committee-established-un-general-assembly-resolution-69-292-development-international-legally-binding-instrument-united-nations-convention-law-sea-conservation-sustainable/";
            },},{id: "library-time-to-act-for-oceans-in-the-2030-agenda-collaborative-partnerships-for-sdg14",
          title: 'Time to act for oceans in the 2030 Agenda: collaborative partnerships for SDG14...',
          description: "Time to act for oceans in the 2030 Agenda: collaborative partnerships for SDG14",
          section: "Library",handler: () => {
              window.location.href = "/library/time-act-oceans-2030-agenda-collaborative-partnerships-sdg14/";
            },},{id: "library-negotiations-for-a-new-agreement-on-the-conservation-and-sustainable-use-of-marine-biodiversity-in-abnj",
          title: 'Negotiations for a new agreement on the conservation and sustainable use of marine...',
          description: "Negotiations for a new agreement on the conservation and sustainable use of marine biodiversity in A...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-negotiations-new-agreement-conservation-sustainable-use-marine-biodiversity-abnj/";
            },},{id: "library-the-partnership-on-science-to-policy-forum",
          title: 'The Partnership on Science to Policy Forum',
          description: "The meeting on the Partnership on Science to Policy Forum was organized by the Secretariat of the Nairobi Convention for the Protection, Management and Development of the Marine and Coastal Environmen...",
          section: "Library",handler: () => {
              window.location.href = "/library/partnership-science-policy-forum/";
            },},{id: "library-the-role-of-science-in-implementing-the-2030-agenda",
          title: 'The Role of Science in Implementing the 2030 Agenda',
          description: "The Role of Science in Implementing the 2030 Agenda",
          section: "Library",handler: () => {
              window.location.href = "/library/role-science-implementing-2030-agenda/";
            },},{id: "library-1ère-réunion-du-groupe-de-réflexion-et-de-travail-sur-la-gouvernance-de-la-haute-mer",
          title: '1ère réunion du groupe de réflexion et de travail sur la gouvernance de...',
          description: "1ère réunion du groupe de réflexion et de travail sur la gouvernance de la haute mer",
          section: "Library",handler: () => {
              window.location.href = "/library/1ere-reunion-du-groupe-de-reflexion-et-de-travail-sur-la-gouvernance-de-la-haute-mer/";
            },},{id: "library-quel-statut-pour-la-haute-mer",
          title: 'Quel statut pour la haute mer ?',
          description: "Quel statut pour la haute mer ?",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-quel-statut-pour-la-haute-mer/";
            },},{id: "library-commocean-2nd-international-marine-science-communication-conference",
          title: 'CommOcean: 2nd International Marine Science Communication Conference',
          description: "CommOcean: 2nd International Marine Science Communication Conference",
          section: "Library",handler: () => {
              window.location.href = "/library/commocean-2nd-international-marine-science-communication-conference/";
            },},{id: "library-achieving-the-sustainable-development-goal-for-the-oceans",
          title: 'Achieving the Sustainable Development Goal for the Oceans',
          description: "The United Nations 2030 Agenda for Sustainable Development and its comprehensive set of 17 interlinking Sustainable Development Goals (SDGs) offer a unique opportunity to advance ocean sustainability....",
          section: "Library",handler: () => {
              window.location.href = "/library/achieving-sustainable-development-goal-oceans/";
            },},{id: "library-consenting-ocean-energy-projects-issues-challenges-and-opportunities",
          title: 'Consenting ocean energy projects: Issues, challenges and opportunities',
          description: "Consenting ocean energy projects: Issues, challenges and opportunities",
          section: "Library",handler: () => {
              window.location.href = "/library/consenting-ocean-energy-projects-issues-challenges-opportunities/";
            },},{id: "library-environmental-impact-assessment-in-areas-beyond-national-jurisdiction-options-for-a-new-international-agreement",
          title: 'Environmental Impact Assessment in Areas beyond National Jurisdiction: Options for a New International...',
          description: "Environmental Impact Assessment in Areas beyond National Jurisdiction: Options for a New Internation...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-environmental-impact-assessment-areas-beyond-national-jurisdiction-options-new-international-agreement/";
            },},{id: "library-partnering-for-a-sustainable-ocean-the-role-of-regional-ocean-governance-in-implementing-sdg14",
          title: 'Partnering for a Sustainable Ocean: The Role of Regional Ocean Governance in Implementing...',
          description: "This report highlights the relevance of regional ocean governance (ROG) for the implementation of the 2030 Agenda, the achievement of SDG14, and the transition to ecosystem-based management more gener...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-partnering-sustainable-ocean-role-regional-ocean-governance-implementing-sdg14/";
            },},{id: "library-regional-management-of-areas-beyond-national-jurisdiction-in-the-western-indian-ocean-state-of-play-and-possible-ways-forward",
          title: 'Regional Management of Areas beyond National Jurisdiction in the Western Indian Ocean: State...',
          description: "Regional Management of Areas beyond National Jurisdiction in the Western Indian Ocean: State of Play...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-regional-management-areas-beyond-national-jurisdiction-western-indian-ocean-state-play-possible-ways-forward/";
            },},{id: "library-risky-business-enterprise-liability-corporate-groups-and-torts",
          title: 'Risky Business: Enterprise Liability, Corporate Groups and Torts',
          description: "Risky Business: Enterprise Liability, Corporate Groups and Torts",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-risky-business-enterprise-liability-corporate-groups-torts/";
            },},{id: "library-marine-planning-an-ocean-energy-perspective",
          title: 'Marine planning: an ocean energy perspective',
          description: "Marine planning: an ocean energy perspective",
          section: "Library",handler: () => {
              window.location.href = "/library/marine-planning-ocean-energy-perspective/";
            },},{id: "library-ocean-energy-governance-challenges-for-wave-and-tidal-stream-technologies",
          title: 'Ocean Energy: Governance Challenges for Wave and Tidal Stream Technologies',
          description: "Ocean Energy: Governance Challenges for Wave and Tidal Stream Technologies",
          section: "Library",handler: () => {
              window.location.href = "/library/ocean-energy-governance-challenges-wave-tidal-stream-technologies/";
            },},{id: "library-regional-launch-of-western-indian-ocean-economy-report-and-presentation-of-madagascar-s-vision-on-ocean-governance",
          title: 'Regional launch of Western Indian Ocean Economy Report and presentation of Madagascar’s vision...',
          description: "Regional launch of Western Indian Ocean Economy Report and presentation of Madagascar’s vision on Oc...",
          section: "Library",handler: () => {
              window.location.href = "/library/regional-launch-western-indian-ocean-economy-report-presentation-madagascars-vision-ocean-governance/";
            },},{id: "library-2nd-international-conference-on-marine-maritime-spatial-planning",
          title: '2nd International Conference on Marine/Maritime Spatial Planning',
          description: "2nd International Conference on Marine/Maritime Spatial Planning",
          section: "Library",handler: () => {
              window.location.href = "/library/2nd-international-conference-marine-maritime-spatial-planning/";
            },},{id: "library-environmental-impact-assessment-in-areas-beyond-national-jurisdiction-challenges-and-opportunities-for-small-island-developing-states",
          title: 'Environmental impact assessment in Areas Beyond National Jurisdiction: challenges and opportunities for Small-Island...',
          description: "Environmental impact assessment in Areas Beyond National Jurisdiction: challenges and opportunities ...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-environmental-impact-assessment-areas-beyond-national-jurisdiction-challenges-opportunities-small-island-developing-states/";
            },},{id: "library-partnering-for-a-sustainable-ocean-the-role-of-regional-ocean-governance-in-implementing-sdg14",
          title: 'Partnering for a Sustainable Ocean: The Role of Regional Ocean Governance in Implementing...',
          description: "Partnering for a Sustainable Ocean: The Role of Regional Ocean Governance in Implementing SDG14",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-partnering-sustainable-ocean-role-regional-ocean-governance-implementing-sdg14/";
            },},{id: "library-third-session-of-the-preparatory-committee-established-by-the-un-general-assembly-resolution-69-292-development-of-an-international-legally-binding-instrument-under-the-united-nations-convention-on-the-law-of-the-sea-on-the-conservation-and-sustainable-use-of-marine-biological-diversity-of-areas-beyond-national-jurisdiction",
          title: 'Third Session of the Preparatory Committee Established by the UN General Assembly Resolution...',
          description: "Third Session of the Preparatory Committee Established by the UN General Assembly Resolution 69/292 ...",
          section: "Library",handler: () => {
              window.location.href = "/library/third-session-preparatory-committee-established-un-general-assembly-resolution-69-292-development-international-legally-binding-instrument-united-nations-convention-law-sea-conservation-sustainable/";
            },},{id: "library-biodiversity-beyond-national-jurisdictions-area-based-management-tools-including-marine-protected-areas",
          title: 'Biodiversity Beyond National Jurisdictions: Area-based Management Tools, including Marine Protected Areas',
          description: "Biodiversity Beyond National Jurisdictions: Area-based Management Tools, including Marine Protected ...",
          section: "Library",handler: () => {
              window.location.href = "/library/biodiversity-beyond-national-jurisdictions-area-based-management-tools-including-marine-protected-areas/";
            },},{id: "library-dixième-réunion-du-groupe-national-informel-haute-mer",
          title: 'Dixième réunion du Groupe national informel haute mer',
          description: "Dixième réunion du Groupe national informel haute mer",
          section: "Library",handler: () => {
              window.location.href = "/library/dixieme-reunion-du-groupe-national-informel-haute-mer/";
            },},{id: "library-oceans-in-the-2030-agenda-the-role-of-regional-governance",
          title: 'Oceans in the 2030 Agenda: The role of Regional Governance',
          description: "Oceans in the 2030 Agenda: The role of Regional Governance",
          section: "Library",handler: () => {
              window.location.href = "/library/oceans-2030-agenda-role-regional-governance/";
            },},{id: "library-united-nations-ocean-conference",
          title: 'United Nations Ocean Conference',
          description: "United Nations Ocean Conference",
          section: "Library",handler: () => {
              window.location.href = "/library/united-nations-ocean-conference/";
            },},{id: "library-fourth-session-of-the-preparatory-committee-established-by-the-un-general-assembly-resolution-69-292-development-of-an-international-legally-binding-instrument-under-the-united-nations-convention-on-the-law-of-the-sea-on-the-conservation-and-sustainable-use-of-marine-biological-diversity-of-areas-beyond-national-jurisdiction",
          title: 'Fourth Session of the Preparatory Committee Established by the UN General Assembly Resolution...',
          description: "Fourth Session of the Preparatory Committee Established by the UN General Assembly Resolution 69/292...",
          section: "Library",handler: () => {
              window.location.href = "/library/fourth-session-preparatory-committee-established-un-general-assembly-resolution-69-292-development-international-legally-binding-instrument-united-nations-convention-law-sea-conservation-sustainable/";
            },},{id: "library-coming-soon-towards-formal-negotiations-for-a-agreement-on-high-seas-governance",
          title: 'Coming soon: towards formal negotiations for a agreement on high seas governance',
          description: "Late in the evening of Friday, 21 July, States meeting at the UN headquarters in New York quietly took a significant step in a longrunning process aiming to close gaps in the international rules cover...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-coming-soon-towards-formal-negotiations-agreement-high-seas-governance/";
            },},{id: "library-our-ocean",
          title: 'Our Ocean',
          description: "Our Ocean",
          section: "Library",handler: () => {
              window.location.href = "/library/ocean/";
            },},{id: "library-areas-beyond-national-jurisdiction-in-the-western-indian-ocean-options-for-governance-amp-management",
          title: 'Areas Beyond National Jurisdiction in the Western Indian Ocean: Options for Governance &amp;amp;...',
          description: "Areas Beyond National Jurisdiction in the Western Indian Ocean: Options for Governance &amp; Management",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-areas-beyond-national-jurisdiction-western-indian-ocean-options-governance-management/";
            },},{id: "library-protecting-our-blue-planet-too-the-year-in-ocean-conservation",
          title: 'Protecting our Blue Planet too: the year in ocean conservation',
          description: "Protecting our Blue Planet too: the year in ocean conservation - watched in awe as Sir David Attenborough and the Blue Planet II team showed us spellbinding images of an underwater world.",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-protecting-blue-planet-too-year-ocean-conservation/";
            },},{id: "library-high-seas-governance-understanding-the-upcoming-negotiations-in-10-points",
          title: 'High seas governance: Understanding the upcoming negotiations in 10 points',
          description: "The United Nations General Assembly just launched a new initiative to address the increasing number of threats to marine areas beyond national jurisdiction (ABNJ). Negotiations will commence in 2018 t...",
          section: "Library",handler: () => {
              window.location.href = "/library/high-seas-governance-understanding-upcoming-negotiations-10-points/";
            },},{id: "library-potsdam-ocean-governance-workshop-the-ocean-in-2030-how-to-get-to-the-future-we-want",
          title: 'Potsdam Ocean Governance Workshop: The Ocean in 2030 – How to get to...',
          description: "Potsdam Ocean Governance Workshop: The Ocean in 2030 – How to get to the future we want?",
          section: "Library",handler: () => {
              window.location.href = "/library/potsdam-ocean-governance-workshop-ocean-2030-how-get-future-want/";
            },},{id: "library-conservation-and-sustainable-use-of-marine-biodiversity-in-areas-beyond-national-jurisdiction-options-for-underpinning-a-strong-global-bbnj-agreement-through-regional-and-sectoral-governance",
          title: 'Conservation and Sustainable Use of Marine Biodiversity in Areas Beyond National Jurisdiction: Options...',
          description: "Gjerde, K., Boteler, B., Durussel, C., Rochette, J., Unger, S., Wright‚ G., ‘Conservation and Sustainable Use of Marine Biodiversity in Areas Beyond National Jurisdiction: Options for Underpinning a S...",
          section: "Library",handler: () => {
              window.location.href = "/library/conservation-sustainable-use-marine-biodiversity-areas-beyond-national-jurisdiction-options-underpinning-strong-global-bbnj-agreement-regional-sectoral-governance/";
            },},{id: "library-academia-obscura-the-hidden-silly-side-of-higher-education",
          title: 'Academia Obscura: The Hidden Silly Side of Higher Education',
          description: "Academia Obscura: The Hidden Silly Side of Higher Education",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-academia-obscura-hidden-silly-side-higher-education/";
            },},{id: "library-the-long-and-winding-road-negotiating-a-treaty-for-the-conservation-and-sustainable-use-of-marine-biodiversity-in-areas-beyond-national-jurisdiction",
          title: 'The Long and Winding Road: negotiating a treaty for the conservation and sustainable...',
          description: "Marine areas beyond national jurisdiction (ABNJ) cover nearly half of the Earth’s surface and host a significant portion of its biodiversity. The international community, increasingly aware of the gro...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-long-winding-road-negotiating-treaty-conservation-sustainable-use-marine-biodiversity-areas-beyond-national-jurisdiction/";
            },},{id: "library-laying-the-foundations-for-management-of-a-seamount-beyond-national-jurisdiction-a-case-study-of-the-walters-shoal-in-the-south-west-indian-ocean",
          title: 'Laying the Foundations for Management of a Seamount Beyond National Jurisdiction: A case...',
          description: "Laying the Foundations for Management of a Seamount Beyond National Jurisdiction: A case study of th...",
          section: "Library",handler: () => {
              window.location.href = "/library/laying-foundations-management-seamount-beyond-national-jurisdiction-case-walters-shoal-south-west-indian-ocean/";
            },},{id: "library-strategic-environmental-assessment-sea-envisioning-its-application-to-marine-areas-beyond-national-jurisdiction-abnj",
          title: 'Strategic Environmental Assessment (SEA). Envisioning its Application to Marine Areas beyond National Jurisdiction...',
          description: "Strategic Environmental Assessment (SEA). Envisioning its Application to Marine Areas beyond Nationa...",
          section: "Library",handler: () => {
              window.location.href = "/library/strategic-environmental-assessment-sea-envisioning-application-marine-areas-beyond-national-jurisdiction-abnj/";
            },},{id: "library-strengthening-regional-ocean-governance-for-the-high-seas-opportunities-and-challenges-to-improve-the-legal-and-institutional-framework-of-the-southeast-atlantic-and-southeast-pacific",
          title: 'Strengthening Regional Ocean Governance for the High Seas: Opportunities and Challenges to Improve...',
          description: "The Southeast Atlantic and Southeast Pacific regions are both characterised by their high biological productivity, supported by important oceanic currents. Recognising the need to ensure conservation ...",
          section: "Library",handler: () => {
              window.location.href = "/library/strengthening-regional-ocean-governance-high-seas-opportunities-challenges-improve-legal-institutional-framework-southeast-atlantic-southeast-pacific/";
            },},{id: "library-protect-the-neglected-half-of-our-blue-planet",
          title: 'Protect the neglected half of our blue planet',
          description: "At the close of 2017, 14 million UK viewers tuned into the acclaimed second series of David Attenborough’s Blue Planet, making it the year’s most-watched television show. It brought the wonders of the...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-protect-neglected-half-blue-planet/";
            },},{id: "library-international-network-for-social-studies-of-marine-energy-issmer-shape-workshop-social-sciences-and-humanities-for-advancing-policy-in-european-energy",
          title: 'International network for Social Studies of Marine Energy (ISSMER) SHAPE workshop (Social Sciences...',
          description: "International network for Social Studies of Marine Energy (ISSMER) SHAPE workshop (Social Sciences a...",
          section: "Library",handler: () => {
              window.location.href = "/library/international-network-social-studies-marine-energy-issmer-shape-workshop-social-sciences-humanities-advancing-policy-european-energy/";
            },},{id: "library-gobernanza-regional-en-las-zonas-fuera-de-la-jurisdicción-nacional-qué-aprendimos-y-cómo-avanzar",
          title: 'Gobernanza regional en las zonas fuera de la jurisdicción nacional: Qué aprendimos y...',
          description: "Gobernanza regional en las zonas fuera de la jurisdicción nacional: Qué aprendimos y cómo avanzar",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-gobernanza-regional-en-las-zonas-fuera-de-la-jurisdiccion-nacional-que-aprendimos-y-como-avanzar/";
            },},{id: "library-second-meeting-of-the-sustainable-ocean-initiative-global-dialogue-with-regional-seras-organizations-and-regional-fisheries-bodies-on-accelerating-progress-towards-the-aichi-biodiversity-targets-and-sustainable-development-goals",
          title: 'Second Meeting of the Sustainable Ocean Initiative Global Dialogue with Regional Seras Organizations...',
          description: "Second Meeting of the Sustainable Ocean Initiative Global Dialogue with Regional Seras Organizations...",
          section: "Library",handler: () => {
              window.location.href = "/library/second-meeting-sustainable-ocean-initiative-global-dialogue-regional-seras-organizations-regional-fisheries-bodies-accelerating-progress-towards-aichi-biodiversity-targets-sustainable-development/";
            },},{id: "library-area-based-management-tools",
          title: 'Area-based management tools',
          description: "Area-based management tools",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-area-based-management-tools/";
            },},{id: "library-regional-amp-global-governance-of-areas-beyond-national-jurisdiction",
          title: 'Regional &amp;amp; Global Governance of Areas Beyond National Jurisdiction',
          description: "Regional &amp; Global Governance of Areas Beyond National Jurisdiction",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-regional-global-governance-areas-beyond-national-jurisdiction/";
            },},{id: "library-high-seas-governance-and-fisheries-management",
          title: 'High seas governance and fisheries management',
          description: "High seas governance and fisheries management",
          section: "Library",handler: () => {
              window.location.href = "/library/high-seas-governance-fisheries-management/";
            },},{id: "library-making-reform-happen-for-sustainable-fisheries",
          title: 'Making reform happen for sustainable fisheries',
          description: "Making reform happen for sustainable fisheries",
          section: "Library",handler: () => {
              window.location.href = "/library/making-reform-happen-sustainable-fisheries/";
            },},{id: "library-marine-planning-on-the-high-seas",
          title: 'Marine Planning on the High Seas',
          description: "Marine Planning on the High Seas",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-marine-planning-high-seas/";
            },},{id: "library-opportunities-for-strengthening-ocean-governance-in-the-southeast-pacific",
          title: 'Opportunities for Strengthening Ocean Governance in the Southeast Pacific',
          description: "Opportunities for Strengthening Ocean Governance in the Southeast Pacific",
          section: "Library",handler: () => {
              window.location.href = "/library/opportunities-strengthening-ocean-governance-southeast-pacific/";
            },},{id: "library-pollution-des-océans-le-problème-est-il-sous-estimé",
          title: 'Pollution des océans: le problème est-il sous-estimé ?',
          description: "Pollution des océans: le problème est-il sous-estimé ?",
          section: "Library",handler: () => {
              window.location.href = "/library/pollution-des-oceans-le-probleme-est-il-sous-estime/";
            },},{id: "library-technological-tools-for-monitoring-control-and-surveillance-in-marine-areas-beyond-national-jurisdiction",
          title: 'Technological tools for Monitoring, Control and Surveillance in Marine Areas Beyond National Jurisdiction...',
          description: "Monitoring Control and Surveillance (MCS) will be crucial to ensuring compliance with management measures developed under a future international agreement on Areas Beyond National Jurisdiction (ABNJ)....",
          section: "Library",handler: () => {
              window.location.href = "/library/technological-tools-monitoring-control-surveillance-marine-areas-beyond-national-jurisdiction/";
            },},{id: "library-bbnj-training-for-un-negotiations",
          title: 'BBNJ Training for UN Negotiations',
          description: "BBNJ Training for UN Negotiations",
          section: "Library",handler: () => {
              window.location.href = "/library/bbnj-training-un-negotiations/";
            },},{id: "library-building-a-strong-high-seas-treaty-what-is-the-role-for-regional-ocean-governance",
          title: 'Building a Strong High Seas Treaty - What is the Role for Regional...',
          description: "Building a Strong High Seas Treaty - What is the Role for Regional Ocean Governance?",
          section: "Library",handler: () => {
              window.location.href = "/library/building-strong-high-seas-treaty-what-role-regional-ocean-governance/";
            },},{id: "library-capacity-building-workshop-un-biodiversity-beyond-national-jurisdiction-bbnj-negotiations",
          title: 'Capacity Building Workshop: UN Biodiversity Beyond National Jurisdiction (BBNJ) Negotiations',
          description: "Capacity Building Workshop: UN Biodiversity Beyond National Jurisdiction (BBNJ) Negotiations",
          section: "Library",handler: () => {
              window.location.href = "/library/capacity-building-workshop-un-biodiversity-beyond-national-jurisdiction-bbnj-negotiations/";
            },},{id: "library-first-session-of-the-intergovernmental-conference-on-an-international-legally-binding-instrument-under-the-united-nations-convention-on-the-law-of-the-sea-on-the-conservation-and-sustainable-use-of-marine-biological-diversity-of-areas-beyond-national-jurisdiction",
          title: 'First session of the Intergovernmental conference on an international legally binding instrument under...',
          description: "First session of the Intergovernmental conference on an international legally binding instrument und...",
          section: "Library",handler: () => {
              window.location.href = "/library/first-session-intergovernmental-conference-international-legally-binding-instrument-united-nations-convention-law-sea-conservation-sustainable-use-marine-biological-diversity-areas-beyond-national/";
            },},{id: "library-bbnj-negotiations-state-of-play",
          title: 'BBNJ Negotiations: State of play',
          description: "BBNJ Negotiations: State of play",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-bbnj-negotiations-state-play/";
            },},{id: "library-role-of-technology-and-monitoring-control-and-surveillance-in-marine-conservation-and-management",
          title: 'Role of technology and Monitoring, Control and Surveillance in Marine Conservation and Management...',
          description: "Role of technology and Monitoring, Control and Surveillance in Marine Conservation and Management",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-role-technology-monitoring-control-surveillance-marine-conservation-management/";
            },},{id: "library-marine-spatial-planning-in-areas-beyond-national-jurisdiction-opportunities-and-challenges",
          title: 'Marine Spatial Planning in Areas Beyond National Jurisdiction: Opportunities and challenges',
          description: "Marine Spatial Planning in Areas Beyond National Jurisdiction: Opportunities and challenges",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-marine-spatial-planning-areas-beyond-national-jurisdiction-opportunities-challenges/";
            },},{id: "library-underpinning-a-high-seas-treaty-through-strong-regional-and-sectoral-governance",
          title: 'Underpinning a High Seas Treaty through Strong Regional and Sectoral Governance',
          description: "Underpinning a High Seas Treaty through Strong Regional and Sectoral Governance",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-underpinning-high-seas-treaty-strong-regional-sectoral-governance/";
            },},{id: "library-high-level-expert-meeting-building-a-strong-high-seas-treaty-what-is-the-role-for-regional-ocean-governance",
          title: 'High-Level Expert Meeting: Building a Strong High Seas Treaty: What is the Role...',
          description: "High-Level Expert Meeting: Building a Strong High Seas Treaty: What is the Role for Regional Ocean G...",
          section: "Library",handler: () => {
              window.location.href = "/library/high-level-expert-meeting-building-strong-high-seas-treaty-what-role-regional-ocean-governance/";
            },},{id: "library-vers-une-protection-de-la-haute-mer",
          title: 'Vers une protection de la haute mer',
          description: "Un traité international devrait mieux protéger la haute mer, de plus en plus touchée par l’activité humaine. Mais le processus reste encore long.",
          section: "Library",handler: () => {
              window.location.href = "/library/vers-une-protection-de-la-haute-mer/";
            },},{id: "library-fisheries-in-a-new-high-seas-treaty-opportunities-and-challenges",
          title: 'Fisheries in a new high seas treaty: Opportunities and challenges',
          description: "Fisheries in a new high seas treaty: Opportunities and challenges",
          section: "Library",handler: () => {
              window.location.href = "/library/fisheries-new-high-seas-treaty-opportunities-challenges/";
            },},{id: "library-exploring-the-world-heritage-convention-for-high-seas-conservation",
          title: 'Exploring the World Heritage Convention for High Seas Conservation',
          description: "Exploring the World Heritage Convention for High Seas Conservation",
          section: "Library",handler: () => {
              window.location.href = "/library/exploring-world-heritage-convention-high-seas-conservation/";
            },},{id: "library-engaging-audiences-with-a-fun-and-friendly-newsletter-the-little-blue-letter-story",
          title: 'Engaging audiences with a fun and friendly newsletter: The Little Blue Letter Story...',
          description: "Engaging audiences with a fun and friendly newsletter: The Little Blue Letter Story",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-engaging-audiences-fun-friendly-newsletter-little-blue-letter-story/";
            },},{id: "library-achieving-a-healthy-ocean-regional-ocean-governance-beyond-2020-marine-regions-forum-2019-conference-report",
          title: 'Achieving a Healthy Ocean - Regional Ocean Governance Beyond 2020 (Marine Regions Forum...',
          description: "Achieving a Healthy Ocean - Regional Ocean Governance Beyond 2020 (Marine Regions Forum 2019 Confere...",
          section: "Library",handler: () => {
              window.location.href = "/library/achieving-healthy-ocean-regional-ocean-governance-beyond-2020-marine-regions-forum-2019-conference-report/";
            },},{id: "library-high-hopes-for-the-high-seas-beyond-the-package-deal-towards-an-ambitious-treaty",
          title: 'High Hopes for the High Seas: beyond the package deal towards an ambitious...',
          description: "Cognisant of the growing threats to biodiversity in marine areas beyond national jurisdiction (ABNJ), States at the United Nations are negotiating a treaty to ensure the conservation and sustainable u...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-high-hopes-high-seas-beyond-package-deal-towards-ambitious-treaty/";
            },},{id: "library-regional-ocean-governance-of-areas-beyond-national-jurisdiction-lessons-learnt-and-ways-forward",
          title: 'Regional Ocean Governance of Areas Beyond National Jurisdiction: Lessons Learnt and Ways Forward...',
          description: "Regional Ocean Governance of Areas Beyond National Jurisdiction: Lessons Learnt and Ways Forward",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-regional-ocean-governance-areas-beyond-national-jurisdiction-lessons-learnt-ways-forward/";
            },},{id: "library-regional-governance-of-areas-beyond-national-jurisdiction",
          title: 'Regional Governance of Areas Beyond National Jurisdiction',
          description: "Regional Governance of Areas Beyond National Jurisdiction",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-regional-governance-areas-beyond-national-jurisdiction/";
            },},{id: "library-keeping-an-eye-on-the-high-seas-strengthening-monitoring-control-and-surveillance-through-a-new-marine-biodiversity-treaty",
          title: 'Keeping an Eye on the High Seas Strengthening Monitoring, Control and Surveillance through...',
          description: "Effective monitoring, control and surveillance (MCS) is critical for the success of marine conservation and management measures. Whereas States have the exclusive right to manage the marine resources ...",
          section: "Library",handler: () => {
              window.location.href = "/library/keeping-eye-high-seas-strengthening-monitoring-control-surveillance-new-marine-biodiversity-treaty/";
            },},{id: "library-marine-regions-forum-2019-key-messages-achieving-a-healthy-ocean-regional-ocean-governance-beyond-2020",
          title: 'Marine Regions Forum 2019 Key Messages: Achieving a Healthy Ocean - Regional Ocean...',
          description: "Marine Regions Forum 2019 Key Messages: Achieving a Healthy Ocean - Regional Ocean Governance Beyond...",
          section: "Library",handler: () => {
              window.location.href = "/library/marine-regions-forum-2019-key-messages-achieving-healthy-ocean-regional-ocean-governance-beyond-2020/";
            },},{id: "library-towards-ecosystem-based-management-of-the-global-ocean-strengthening-regional-cooperation-through-a-new-agreement-for-the-conservation-and-sustainable-use-of-marine-biodiversity-in-areas-beyond-national-jurisdiction",
          title: 'Towards Ecosystem-based Management of the Global Ocean: Strengthening Regional Cooperation through a New...',
          description: "Towards Ecosystem-based Management of the Global Ocean: Strengthening Regional Cooperation through a...",
          section: "Library",handler: () => {
              window.location.href = "/library/towards-ecosystem-based-management-global-ocean-strengthening-regional-cooperation-new-agreement-conservation-sustainable-use-marine-biodiversity-areas-beyond-national-jurisdiction/";
            },},{id: "library-the-high-seas-how-can-we-govern-half-of-the-planet-for-the-benefit-of-all-the-world-s-people",
          title: 'The high seas: how can we govern half of the planet for the...',
          description: "The high seas: how can we govern half of the  planet for the benefit of all the world’s people?",
          section: "Library",handler: () => {
              window.location.href = "/library/high-seas-how-govern-half-planet-benefit-worlds-people/";
            },},{id: "library-strategic-workshop-towards-an-inclusive-blue-economy",
          title: 'Strategic workshop: towards an inclusive blue economy',
          description: "Strategic workshop: towards an inclusive blue economy",
          section: "Library",handler: () => {
              window.location.href = "/library/strategic-workshop-towards-inclusive-blue-economy/";
            },},{id: "library-connectivity-in-a-future-high-seas-treaty",
          title: 'Connectivity in a Future High Seas Treaty',
          description: "Connectivity in a Future High Seas Treaty",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-connectivity-future-high-seas-treaty/";
            },},{id: "library-overview-of-regional-initiatives-for-the-conservation-and-sustainable-use-of-marine-biodiversity-in-areas-beyond-national-jurisdiction",
          title: 'Overview of regional initiatives for the conservation and sustainable use of marine biodiversity...',
          description: "Overview of regional initiatives for the conservation and sustainable use of marine biodiversity in ...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-overview-regional-initiatives-conservation-sustainable-use-marine-biodiversity-areas-beyond-national-jurisdiction/";
            },},{id: "library-regional-ocean-governance-of-areas-beyond-national-jurisdiction-lessons-learnt-and-ways-forward",
          title: 'Regional Ocean Governance of Areas Beyond National Jurisdiction: Lessons Learnt and Ways Forward...',
          description: "Regional Ocean Governance of Areas Beyond National Jurisdiction: Lessons Learnt and Ways Forward",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-regional-ocean-governance-areas-beyond-national-jurisdiction-lessons-learnt-ways-forward/";
            },},{id: "library-high-level-expert-meeting-towards-an-effective-high-seas-treaty-building-on-and-strengthening-regional-ocean-governance",
          title: 'High-level expert meeting: Towards an Effective High Seas Treaty: Building on and Strengthening...',
          description: "High-level expert meeting: Towards an Effective High Seas Treaty: Building on and Strengthening Regi...",
          section: "Library",handler: () => {
              window.location.href = "/library/high-level-expert-meeting-towards-effective-high-seas-treaty-building-strengthening-regional-ocean-governance/";
            },},{id: "library-science-for-solutions-bringing-stakeholders-together-to-improve-ocean-planning-and-governance-in-abnj-of-the-south-east-pacific",
          title: 'Science for Solutions: Bringing Stakeholders Together to Improve Ocean Planning and Governance in...',
          description: "Science for Solutions: Bringing Stakeholders Together to Improve Ocean Planning and Governance in AB...",
          section: "Library",handler: () => {
              window.location.href = "/library/science-solutions-bringing-stakeholders-together-improve-ocean-planning-governance-abnj-south-east-pacific/";
            },},{id: "library-towards-an-effective-high-seas-treaty-building-on-and-strengthening-regional-ocean-governance",
          title: 'Towards an Effective High Seas Treaty - Building on and Strengthening Regional Ocean...',
          description: "Towards an Effective High Seas Treaty - Building on and Strengthening Regional Ocean Governance",
          section: "Library",handler: () => {
              window.location.href = "/library/towards-effective-high-seas-treaty-building-strengthening-regional-ocean-governance/";
            },},{id: "library-strengthening-monitoring-control-and-surveillance-mcs-through-an-international-instrument-on-high-seas-biodiversity",
          title: 'Strengthening Monitoring, Control and Surveillance (MCS) through an international instrument on high seas...',
          description: "The workshop covered four different themes: improving transparency at sea, lessons learnt from national experiences, lessons learnt from regional experiences and future policy options. During the work...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-strengthening-monitoring-control-surveillance-mcs-international-instrument-high-seas-biodiversity/";
            },},{id: "library-haute-mer-une-version-quot-zéro-quot-du-traité-attendue-d-ici-à-la-fin-juillet",
          title: 'Haute mer : une version &amp;quot;zéro&amp;quot; du traité attendue d’ici à la fin...',
          description: "La deuxième session de négociations sur la préservation et l’utilisation durable de la biodiversité en haute mer s’est conclue le 5 avril dernier. L’occasion...",
          section: "Library",handler: () => {
              window.location.href = "/library/haute-mer-une-version-zero-du-traite-attendue-dici-a-la-fin-juillet/";
            },},{id: "library-la-haute-mer-à-l-épreuve-de-la-diplomatie",
          title: 'La haute mer à l’épreuve de la diplomatie',
          description: "Elle n’appartient à personne et échappe à toute réglementation. Face aux pressions humaines et climatiques, l’Onu tente de négocier un traité sur le statut juridique de cette vaste étendue d’eau pour ...",
          section: "Library",handler: () => {
              window.location.href = "/library/la-haute-mer-a-lepreuve-de-la-diplomatie/";
            },},{id: "library-second-session-of-the-intergovernmental-conference-on-an-international-legally-binding-instrument-under-the-united-nations-convention-on-the-law-of-the-sea-on-the-conservation-and-sustainable-use-of-marine-biological-diversity-of-areas-beyond-national-jurisdiction",
          title: 'Second session of the Intergovernmental conference on an international legally binding instrument under...',
          description: "Second session of the Intergovernmental conference on an international legally binding instrument un...",
          section: "Library",handler: () => {
              window.location.href = "/library/second-session-intergovernmental-conference-international-legally-binding-instrument-united-nations-convention-law-sea-conservation-sustainable-use-marine-biological-diversity-areas-beyond-national/";
            },},{id: "library-building-capacities-for-regional-ocean-governance-marine-genetic-resources-and-area-based-management-tools",
          title: 'Building Capacities for Regional Ocean Governance: Marine Genetic Resources and Area-based Management Tools...',
          description: "Building Capacities for Regional Ocean Governance: Marine Genetic Resources and Area-based Managemen...",
          section: "Library",handler: () => {
              window.location.href = "/library/building-capacities-regional-ocean-governance-marine-genetic-resources-area-based-management-tools/";
            },},{id: "library-les-négociations-sur-la-biodiversité-en-haute-mer-reprennent-à-new",
          title: 'Les négociations sur la biodiversité en haute mer reprennent à New...',
          description: "La troisième session de négociations d’un traité sur la préservation et l’utilisation durable de la biodiversité en haute mer s’ouvre ce lundi 19 août...",
          section: "Library",handler: () => {
              window.location.href = "/library/les-negociations-sur-la-biodiversite-en-haute-mer-reprennent-a-new/";
            },},{id: "library-one-ocean-symposium",
          title: 'One Ocean Symposium',
          description: "One Ocean Symposium",
          section: "Library",handler: () => {
              window.location.href = "/library/one-ocean-symposium/";
            },},{id: "library-third-session-of-the-intergovernmental-conference-on-an-international-legally-binding-instrument-under-the-united-nations-convention-on-the-law-of-the-sea-on-the-conservation-and-sustainable-use-of-marine-biological-diversity-of-areas-beyond-national-jurisdiction",
          title: 'Third session of the Intergovernmental conference on an international legally binding instrument under...',
          description: "Third session of the Intergovernmental conference on an international legally binding instrument und...",
          section: "Library",handler: () => {
              window.location.href = "/library/third-session-intergovernmental-conference-international-legally-binding-instrument-united-nations-convention-law-sea-conservation-sustainable-use-marine-biological-diversity-areas-beyond-national/";
            },},{id: "library-interview-with-ocean-university-initiative",
          title: 'Interview with Ocean University Initiative',
          description: "Interview with Ocean University Initiative",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-interview-ocean-university-initiative/";
            },},{id: "library-high-seas-fish-biodiversity-is-slipping-through-the-governance-net",
          title: 'High-seas fish biodiversity is slipping through the governance net',
          description: "States at the United Nations have begun negotiating a new treaty to strengthen the legal regime for marine biodiversity in areas beyond national jurisdiction. Failure to ensure the full scope of fish ...",
          section: "Library",handler: () => {
              window.location.href = "/library/high-seas-fish-biodiversity-slipping-governance-net/";
            },},{id: "library-traité-sur-la-haute-mer-comment-protéger-les-écosystèmes-marins",
          title: 'Traité sur la haute mer: comment protéger les écosystèmes marins ?',
          description: "Traité sur la haute mer: comment protéger les écosystèmes marins ?",
          section: "Library",handler: () => {
              window.location.href = "/library/traite-sur-la-haute-mer-comment-proteger-les-ecosystemes-marins/";
            },},{id: "library-marine-regions-forum",
          title: 'Marine Regions Forum',
          description: "Marine Regions Forum",
          section: "Library",handler: () => {
              window.location.href = "/library/marine-regions-forum/";
            },},{id: "library-environmental-impact-assessment-in-areas-beyond-national-jurisdiction",
          title: 'Environmental Impact Assessment in Areas Beyond National Jurisdiction',
          description: "Environmental Impact Assessment in Areas Beyond National Jurisdiction",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-environmental-impact-assessment-areas-beyond-national-jurisdiction/";
            },},{id: "library-strengthening-monitoring-control-and-surveillance-mcs-through-an-international-instrument-on-high-seas-biodiversity",
          title: 'Strengthening Monitoring, Control and Surveillance (MCS) through an international instrument on high seas...',
          description: "Strengthening Monitoring, Control and Surveillance (MCS) through an international instrument on high...",
          section: "Library",handler: () => {
              window.location.href = "/library/strengthening-monitoring-control-surveillance-mcs-international-instrument-high-seas-biodiversity/";
            },},{id: "library-2020-a-super-year-for-the-ocean",
          title: '2020: a “Super Year” for the ocean?',
          description: "After the “Blue COP”, whose real political impacts will need to be assessed beyond the strong mobilisation of civil society, 2020 is presented as a “super year” for the ocean, marked with several impo...",
          section: "Library",handler: () => {
              window.location.href = "/library/2020-super-year-ocean/";
            },},{id: "library-combatting-marine-plastic-litter-state-of-play-and-perspectives",
          title: 'Combatting marine plastic litter: state of play and perspectives',
          description: "Combatting marine plastic litter: state of play and perspectives",
          section: "Library",handler: () => {
              window.location.href = "/library/combatting-marine-plastic-litter-state-play-perspectives/";
            },},{id: "library-fishing-in-the-twilight-zone-illuminating-governance-challenges-at-the-next-fisheries-frontier",
          title: 'Fishing in the Twilight Zone: Illuminating governance challenges at the next fisheries frontier...',
          description: "Fishing in the Twilight Zone: Illuminating governance challenges at the next fisheries frontier",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-fishing-twilight-zone-illuminating-governance-challenges-next-fisheries-frontier/";
            },},{id: "library-the-history-of-ocean-power",
          title: 'The History of Ocean Power',
          description: "The History of Ocean Power",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-history-ocean-power/";
            },},{id: "library-options-for-strengthening-monitoring-control-and-surveillance-of-human-activities-in-the-southeast-pacific-region",
          title: 'Options for Strengthening Monitoring, Control and Surveillance of Human Activities in the Southeast...',
          description: "This report provides an overview of a range of ongoing initiatives to improve governance of ABNJ at the regional level, including: novel modalities, such as the “Collective Arrange- ment for the North...",
          section: "Library",handler: () => {
              window.location.href = "/library/options-strengthening-monitoring-control-surveillance-human-activities-southeast-pacific-region/";
            },},{id: "library-a-preliminary-analysis-of-the-draft-high-seas-biodiversity-treaty",
          title: 'A preliminary analysis of the draft high seas biodiversity treaty',
          description: "In 2017, following more than a decade of informal discussions, States at the United Nations decided to convene an intergovernmental conference (IGC) to negotiate an international legally binding instr...",
          section: "Library",handler: () => {
              window.location.href = "/library/preliminary-analysis-draft-high-seas-biodiversity-treaty/";
            },},{id: "library-protecting-sites-of-potential-outstanding-universal-value-in-marine-areas-beyond-national-jurisdiction-the-practical-modalities",
          title: 'Protecting sites of potential Outstanding Universal Value in marine Areas Beyond National Jurisdiction:...',
          description: "Protecting sites of potential Outstanding Universal Value in marine Areas Beyond National Jurisdicti...",
          section: "Library",handler: () => {
              window.location.href = "/library/protecting-sites-potential-outstanding-universal-value-marine-areas-beyond-national-jurisdiction-practical-modalities/";
            },},{id: "library-strengthening-monitoring-control-and-surveillance-in-areas-beyond-national-jurisdiction",
          title: 'Strengthening Monitoring, Control and Surveillance in Areas Beyond National Jurisdiction',
          description: "Monitoring, control and surveillance (MCS) is critical for the success of marine conservation and management, but effective MCS remains challenging. This is especially true for the deep and distant wa...",
          section: "Library",handler: () => {
              window.location.href = "/library/strengthening-monitoring-control-surveillance-areas-beyond-national-jurisdiction/";
            },},{id: "library-technical-but-strategic-reflections-on-the-institutional-mechanisms-of-a-future-high-seas-treaty",
          title: 'Technical but strategic: reflections on the institutional mechanisms of a future High Seas...',
          description: "The negotiations for the development of a legally binding instrument on high seas biodiversity began at the end of 2017 and are currently suspended due to the public health crisis. The negotiations ha...",
          section: "Library",handler: () => {
              window.location.href = "/library/technical-strategic-reflections-institutional-mechanisms-future-high-seas-treaty/";
            },},{id: "library-towards-a-package-marine-biodiversity-beyond-national-jurisdiction",
          title: 'Towards a Package: Marine Biodiversity Beyond National Jurisdiction',
          description: "Towards a Package: Marine Biodiversity Beyond National Jurisdiction",
          section: "Library",handler: () => {
              window.location.href = "/library/towards-package-marine-biodiversity-beyond-national-jurisdiction/";
            },},{id: "library-workshop-on-environmental-impact-assessments-eias-and-strategic-environmental-assessments-seas",
          title: 'Workshop on Environmental Impact Assessments (EIAs) and Strategic Environmental Assessments (SEAs)',
          description: "Workshop on Environmental Impact Assessments (EIAs) and Strategic Environmental Assessments (SEAs)",
          section: "Library",handler: () => {
              window.location.href = "/library/workshop-environmental-impact-assessments-eias-strategic-environmental-assessments-seas/";
            },},{id: "library-ocean-action",
          title: 'Ocean Action',
          description: "Ocean Action",
          section: "Library",handler: () => {
              window.location.href = "/library/ocean-action/";
            },},{id: "library-un-discussions-on-marine-genetic-resources-shape-the-future-of-marine-biotechnology",
          title: 'UN discussions on marine genetic resources shape the future of marine biotechnology',
          description: "The first recorded medicinal use of marine species dates from almost 3000 BCE in China. In 400 BCE, Hippocrates noted the antibiotic properties of sponges and recommended they be applied to soldiers&#39; ...",
          section: "Library",handler: () => {
              window.location.href = "/library/un-discussions-marine-genetic-resources-shape-future-marine-biotechnology/";
            },},{id: "library-marine-plastic-pollution-state-of-play-amp-perspectives",
          title: 'Marine Plastic Pollution: State of Play &amp;amp; Perspectives',
          description: "Plastic pollution of the ocean is now reaching an alarming level, threatening species and ecosystems, affecting the well-being of populations and costing billions of euros every year, in particular th...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-marine-plastic-pollution-state-play-perspectives/";
            },},{id: "library-la-coopération-mondiale-nouveau-défi-dans-la-lutte-contre-la-pollution",
          title: 'La coopération mondiale, nouveau défi dans la lutte contre la pollution...',
          description: "La coopération mondiale, nouveau défi dans la lutte contre la pollution...",
          section: "Library",handler: () => {
              window.location.href = "/library/la-cooperation-mondiale-nouveau-defi-dans-la-lutte-contre-la-pollution/";
            },},{id: "library-les-enjeux-de-coordination-entre-le-futur-traité-haute-mer-et-les-organisations-existantes",
          title: 'Les enjeux de coordination entre le futur traité haute mer et les organisations...',
          description: "Les enjeux de coordination entre le futur traité haute mer et les organisations existantes",
          section: "Library",handler: () => {
              window.location.href = "/library/les-enjeux-de-coordination-entre-le-futur-traite-haute-mer-et-les-organisations-existantes/";
            },},{id: "library-area-based-management-tools-including-marine-protected-areas",
          title: 'Area-based Management Tools (Including Marine Protected Areas)',
          description: "Area-based Management Tools (Including Marine Protected Areas)",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-area-based-management-tools-including-marine-protected-areas/";
            },},{id: "library-the-mesopelagic-zone",
          title: 'The Mesopelagic Zone',
          description: "The Mesopelagic Zone",
          section: "Library",handler: () => {
              window.location.href = "/library/mesopelagic-zone/";
            },},{id: "library-the-ocean-39-s-quot-twilight-zone-quot-climate-risks-at-the-next-fisheries-frontier",
          title: 'The Ocean&amp;#39;s &amp;quot;twilight zone&amp;quot;: climate risks at the next fisheries frontier',
          description: "We have known since the 1970s that the Ocean&#39;s vast mesopelagic, or &quot;twilight&quot;, zone could contain huge quantities of fish. Technological advancements now make exploitation possible and interest is gr...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-oceans-twilight-zone-climate-risks-next-fisheries-frontier/";
            },},{id: "library-strengthening-monitoring-control-and-surveillance-through-a-high-seas-treaty",
          title: 'Strengthening Monitoring Control and Surveillance through a High Seas Treaty',
          description: "The high seas treaty is expected to provide for the establishment of marine protected areas (MPAs) beyond national jurisdiction, but there are significant challenges for ensuring that such areas are t...",
          section: "Library",handler: () => {
              window.location.href = "/library/strengthening-monitoring-control-surveillance-high-seas-treaty/";
            },},{id: "library-fishing-in-the-twilight-zone-illuminating-governance-challenges-at-the-next-fisheries-frontier",
          title: 'Fishing in the Twilight Zone: illuminating governance challenges at the next fisheries frontier...',
          description: "The mesopelagic, or &quot;twilight zone&quot; - the waters of the open ocean at a depth of approximately 150-1,000 metres - hosts significant fish stocks. These fish are unpalatable but proposals are emerging t...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-fishing-twilight-zone-illuminating-governance-challenges-next-fisheries-frontier/";
            },},{id: "library-rights-of-nature-perspectives-for-global-ocean-stewardship",
          title: 'Rights of Nature: Perspectives for Global Ocean Stewardship',
          description: "The development of a new international legally binding instrument for the conservation and sustainable use of marine biodiversity beyond national jurisdiction (BBNJ agreement) is in the final negotiat...",
          section: "Library",handler: () => {
              window.location.href = "/library/rights-nature-perspectives-global-ocean-stewardship/";
            },},{id: "library-strengthening-monitoring-control-and-surveillance-of-human-activities-in-marine-areas-beyond-national-jurisdiction-challenges-and-opportunities-for-an-international-legally-binding-instrument",
          title: 'Strengthening monitoring, control and surveillance of human activities in marine areas beyond national...',
          description: "Monitoring, control and surveillance (MCS) is critical for the success of marine conservation and management. This raises specific challenges in the deep and distant waters of marine areas beyond nati...",
          section: "Library",handler: () => {
              window.location.href = "/library/strengthening-monitoring-control-surveillance-human-activities-marine-areas-beyond-national-jurisdiction-challenges-opportunities-international-legally-binding-instrument/";
            },},{id: "library-ocean-power",
          title: 'Ocean Power',
          description: "Ocean Power",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-ocean-power/";
            },},{id: "library-marine-regions-forum-an-international-stakeholder-forum-to-strengthen-regional-ocean-governance",
          title: 'Marine Regions Forum: An international stakeholder forum to strengthen regional ocean governance',
          description: "Marine Regions Forum: An international stakeholder forum to strengthen regional ocean governance",
          section: "Library",handler: () => {
              window.location.href = "/library/marine-regions-forum-international-stakeholder-forum-strengthen-regional-ocean-governance/";
            },},{id: "library-ocean-governance-and-covid-19-building-resilience-for-marine-regions",
          title: 'Ocean Governance and COVID-19 – Building resilience for marine regions',
          description: "Ocean Governance and COVID-19 – Building resilience for marine regions",
          section: "Library",handler: () => {
              window.location.href = "/library/ocean-governance-covid-19-building-resilience-marine-regions/";
            },},{id: "library-options-for-strengthening-monitoring-control-and-surveillance-of-human-activities-in-the-southeast-atlantic-region",
          title: 'Options for Strengthening Monitoring, Control and Surveillance of Human Activities in the Southeast...',
          description: "Effective monitoring, control and surveillance (MCS) of human activities is critical for the conservation and sustainable use of the ocean. This is particularly important in the Southeast Atlantic, wh...",
          section: "Library",handler: () => {
              window.location.href = "/library/options-strengthening-monitoring-control-surveillance-human-activities-southeast-atlantic-region/";
            },},{id: "library-strengthening-high-seas-governance-through-enhanced-environmental-assessment-processes-a-case-study-of-mesopelagic-fisheries-and-options-for-a-future-bbnj-treaty",
          title: 'Strengthening high seas governance through enhanced environmental assessment processes: A case study of...',
          description: "This report explores the challenges of addressing emerging activities in areas beyond national jurisdiction (ABNJ) through a case study – a hypothetical proposal to develop commercial fisheries in the...",
          section: "Library",handler: () => {
              window.location.href = "/library/strengthening-high-seas-governance-enhanced-environmental-assessment-processes-case-mesopelagic-fisheries-options-future-bbnj-treaty/";
            },},{id: "library-toward-a-strategic-action-roadmap-on-oceans-and-climate-2016-to-2021",
          title: 'Toward a Strategic Action Roadmap on Oceans and Climate: 2016 to 2021',
          description: "Toward a Strategic Action Roadmap on Oceans and Climate: 2016 to 2021",
          section: "Library",handler: () => {
              window.location.href = "/library/toward-strategic-action-roadmap-oceans-climate-2016-2021/";
            },},{id: "library-the-role-of-regional-cooperation-efforts-for-the-high-seas-of-the-southeast-pacific",
          title: 'The Role of Regional Cooperation Efforts for the High Seas of the Southeast...',
          description: "The Role of Regional Cooperation Efforts for the High Seas of the Southeast Pacific",
          section: "Library",handler: () => {
              window.location.href = "/library/role-regional-cooperation-efforts-high-seas-southeast-pacific/";
            },},{id: "library-high-hopes-for-the-high-seas-protecting-biodiversity-in-the-global-ocean",
          title: 'High Hopes for the High Seas: Protecting biodiversity in the global ocean',
          description: "High Hopes for the High Seas: Protecting biodiversity in the global ocean",
          section: "Library",handler: () => {
              window.location.href = "/library/high-hopes-high-seas-protecting-biodiversity-global-ocean/";
            },},{id: "library-strengthening-monitoring-control-and-surveillance-through-a-high-seas-treaty",
          title: 'Strengthening Monitoring, Control and Surveillance through a High Seas Treaty',
          description: "Strengthening Monitoring, Control and Surveillance through a High Seas Treaty",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-strengthening-monitoring-control-surveillance-high-seas-treaty/";
            },},{id: "library-ensuring-effective-implementation-of-a-high-seas-biodiversity-treaty-lessons-learned-and-options-for-an-implementation-and-compliance-committee",
          title: 'Ensuring Effective Implementation of a High Seas Biodiversity Treaty: Lessons Learned and Options...',
          description: "Ensuring Effective Implementation of a High Seas Biodiversity Treaty: Lessons Learned and Options fo...",
          section: "Library",handler: () => {
              window.location.href = "/library/ensuring-effective-implementation-high-seas-biodiversity-treaty-lessons-learned-options-implementation-compliance-committee/";
            },},{id: "library-getting-beyond-yes-fast-tracking-implementation-of-the-united-nations-agreement-for-marine-biodiversity-beyond-national-jurisdiction",
          title: 'Getting Beyond Yes: Fast-tracking Implementation of the United Nations Agreement for Marine Biodiversity...',
          description: "With a new international agreement on the conservation and sustainable use of marine biodiversity of areas beyond national jurisdiction (BBNJ Agreement) on the horizon, now is the time to start laying...",
          section: "Library",handler: () => {
              window.location.href = "/library/getting-beyond-yes-fast-tracking-implementation-united-nations-agreement-marine-biodiversity-beyond-national-jurisdiction/";
            },},{id: "library-briefing-for-negotiators-ensuring-effective-implementation-of-a-high-seas-biodiversity-treaty",
          title: 'Briefing for negotiators: Ensuring Effective Implementation of a High Seas Biodiversity Treaty',
          description: "Briefing for negotiators: Ensuring Effective Implementation of a High Seas Biodiversity Treaty",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-briefing-negotiators-ensuring-effective-implementation-high-seas-biodiversity-treaty/";
            },},{id: "library-conserving-the-global-ocean-initial-indications-for-effective-area-based-management-tools-on-the-high-seas",
          title: 'Conserving the Global Ocean: Initial Indications for Effective Area-based Management Tools on the...',
          description: "Conserving the Global Ocean: Initial Indications for Effective Area-based Management Tools on the Hi...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-conserving-global-ocean-initial-indications-effective-area-based-management-tools-high-seas/";
            },},{id: "library-digging-deep-critical-questions-remain-in-the-rush-to-regulate-seabed-mining",
          title: 'Digging deep: critical questions remain in the rush to regulate seabed mining',
          description: "The 1982 United Nations Convention on the Law of the Sea (UNCLOS) defines areas of maritime jurisdiction and sets out the rights and obligations of States, thus serving as a “Constitution for the ocea...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-digging-deep-critical-questions-remain-rush-regulate-seabed-mining/";
            },},{id: "library-summary-report-inter-regional-dialogues-on-high-seas-governance",
          title: 'Summary report: Inter-regional Dialogues on High Seas Governance',
          description: "Member States at the United Nations (UN) are currently negotiating a new treaty for the conservation and sustainable use of high seas biodiversity in areas beyond national jurisdiction (ABNJ). While i...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-summary-report-inter-regional-dialogues-high-seas-governance/";
            },},{id: "library-high-seas-marine-protected-areas-vast-remote-and-costly",
          title: 'High Seas Marine Protected Areas: Vast, Remote and Costly?',
          description: "Organised by IDDRI in the context of the STRONG High Seas project, in cooperation with the International Monitoring, Control and Surveillance (IMCS) Network and the International Union for Conservatio...",
          section: "Library",handler: () => {
              window.location.href = "/library/high-seas-marine-protected-areas-vast-remote-costly/";
            },},{id: "library-biodiversité-en-haute-mer-le-traité-reste-hors-de-portée-malgré-une",
          title: 'Biodiversité en haute mer : le traité reste hors de portée malgré une......',
          description: "Ce que les observateurs pressentaient début mars s’est vérifié: à New York, la quatrième session de négociations sur le futur traité international sur...",
          section: "Library",handler: () => {
              window.location.href = "/library/biodiversite-en-haute-mer-le-traite-reste-hors-de-portee-malgre-une/";
            },},{id: "library-chair-and-students-roundtable-ocean-governance-challenges-and-opportunities",
          title: 'Chair and Students’ Roundtable: Ocean Governance Challenges and Opportunities',
          description: "The third Chair and Students’ Roundtable was held on February 24. It was a virtual event. The topic was “Ocean Governance Challenges and Opportunities”. We were delighted to welcome Glen Wright (PSIA ...",
          section: "Library",handler: () => {
              window.location.href = "/library/chair-students-roundtable-ocean-governance-challenges-opportunities/";
            },},{id: "library-fourth-session-of-the-intergovernmental-conference-on-an-international-legally-binding-instrument-under-the-united-nations-convention-on-the-law-of-the-sea-on-the-conservation-and-sustainable-use-of-marine-biological-diversity-of-areas-beyond-national-jurisdiction",
          title: 'Fourth session of the Intergovernmental conference on an international legally binding instrument under...',
          description: "Fourth session of the Intergovernmental conference on an international legally binding instrument un...",
          section: "Library",handler: () => {
              window.location.href = "/library/fourth-session-intergovernmental-conference-international-legally-binding-instrument-united-nations-convention-law-sea-conservation-sustainable-use-marine-biological-diversity-areas-beyond-national/";
            },},{id: "library-la-quatrième-session-de-négociations-sur-le-futur-traité-de-protection",
          title: 'La quatrième session de négociations sur le futur traité de protection...',
          description: "Après une pause de plus de deux ans et demi due à la pandémie de Covid-19, les négociations sur le futur traité international sur la préservation et l’utilisation...",
          section: "Library",handler: () => {
              window.location.href = "/library/la-quatrieme-session-de-negociations-sur-le-futur-traite-de-protection/";
            },},{id: "library-towards-integrated-ocean-management-of-the-high-seas-lessons-learnt-for-regional-and-global-action",
          title: 'Towards Integrated Ocean Management of the High Seas: Lessons Learnt for Regional and...',
          description: "Towards Integrated Ocean Management of the High Seas: Lessons Learnt for Regional and Global Action",
          section: "Library",handler: () => {
              window.location.href = "/library/towards-integrated-ocean-management-high-seas-lessons-learnt-regional-global-action/";
            },},{id: "library-from-commitment-to-action-exploring-ocean-linked-political-and-finance-solutions-to-climate-change",
          title: 'From Commitment to Action: Exploring Ocean-Linked Political and Finance Solutions to Climate Change...',
          description: "From Commitment to Action: Exploring Ocean-Linked Political and Finance Solutions to Climate Change",
          section: "Library",handler: () => {
              window.location.href = "/library/commitment-action-exploring-ocean-linked-political-finance-solutions-climate-change/";
            },},{id: "library-areas-beyond-national-jurisdiction",
          title: 'Areas Beyond National Jurisdiction',
          description: "Areas Beyond National Jurisdiction",
          section: "Library",handler: () => {
              window.location.href = "/library/areas-beyond-national-jurisdiction/";
            },},{id: "library-high-seas-treaty-dialogues",
          title: 'High Seas Treaty Dialogues',
          description: "High Seas Treaty Dialogues",
          section: "Library",handler: () => {
              window.location.href = "/library/high-seas-treaty-dialogues/";
            },},{id: "library-meeso-modelling-amp-stakeholder-concern-workshop",
          title: 'MEESO Modelling &amp;amp; stakeholder concern workshop',
          description: "MEESO Modelling &amp; stakeholder concern workshop",
          section: "Library",handler: () => {
              window.location.href = "/library/meeso-modelling-stakeholder-concern-workshop/";
            },},{id: "library-marine-spatial-planning",
          title: 'Marine Spatial Planning',
          description: "Marine Spatial Planning",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-marine-spatial-planning/";
            },},{id: "library-oceans-as-archives",
          title: 'Oceans as Archives',
          description: "The Oceans as Archives conference contributes to the growing field of critical ocean studies, while intervening in the erasures and occlusions performed in scripting the field as a new terrain of inqu...",
          section: "Library",handler: () => {
              window.location.href = "/library/oceans-as-archives/";
            },},{id: "library-biodiversité-en-haute-mer-cinquième-et-potentiel-dernier-round-pour",
          title: 'Biodiversité en haute mer : cinquième et potentiel dernier round pour...',
          description: "La 5e et potentielle dernière session de négociations sur le futur traité international sur la conservation et l’utilisation durable de la biodiversité...",
          section: "Library",handler: () => {
              window.location.href = "/library/biodiversite-en-haute-mer-cinquieme-et-potentiel-dernier-round-pour/";
            },},{id: "library-biodiversité-en-haute-mer-craintes-sur-l-ambition-des-aires-marines",
          title: 'Biodiversité en haute mer : craintes sur l’ambition des aires marines...',
          description: "Les négociations sur le traité de conservation et d’utilisation durable de la biodiversité en haute mer sont entrées dans une nouvelle phase avec la publication,...",
          section: "Library",handler: () => {
              window.location.href = "/library/biodiversite-en-haute-mer-craintes-sur-lambition-des-aires-marines/";
            },},{id: "library-fifth-session-of-the-intergovernmental-conference-on-an-international-legally-binding-instrument-under-the-united-nations-convention-on-the-law-of-the-sea-on-the-conservation-and-sustainable-use-of-marine-biological-diversity-of-areas-beyond-national-jurisdiction",
          title: 'Fifth session of the Intergovernmental conference on an international legally binding instrument under...',
          description: "Fifth session of the Intergovernmental conference on an international legally binding instrument und...",
          section: "Library",handler: () => {
              window.location.href = "/library/fifth-session-intergovernmental-conference-international-legally-binding-instrument-united-nations-convention-law-sea-conservation-sustainable-use-marine-biological-diversity-areas-beyond-national/";
            },},{id: "library-a-high-seas-treaty-on-the-horizon-progress-and-prospects-for-the-intergovernmental-conference",
          title: 'A High Seas Treaty on the Horizon: Progress and Prospects for the Intergovernmental...',
          description: "After more than a decade of discussions, States at the United Nations are nearing agreement on a new international legally binding instrument for the conservation and sustainable use of biodiversity i...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-high-seas-treaty-horizon-progress-prospects-intergovernmental-conference/";
            },},{id: "library-the-ship-has-reached-the-shore-quot-why-the-historic-agreement-to-protect-the-high-seas-matters-and-what-happens-next",
          title: 'The ship has reached the shore&amp;quot;: why the historic Agreement to protect the...',
          description: "On Saturday March 4, 2023, the President of the Intergovernmental Conference (IGC) tasked with elaborating an Agreement to protect global ocean biodiversity declared, “The ship has reached the shore”....",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-etal-the-ship-reached-shore-why-historic-agreement-protect-high-seas-matters-what-happens-next/";
            },},{id: "library-initial-reflections-to-support-rapid-effective-and-equitable-implementation-of-the-bbnj-agreement",
          title: 'Initial reflections to support rapid, effective and equitable implementation of the BBNJ Agreement...',
          description: "Initial reflections to support rapid, effective and equitable implementation of the BBNJ Agreement",
          section: "Library",handler: () => {
              window.location.href = "/library/initial-reflections-support-rapid-effective-equitable-implementation-bbnj-agreement/";
            },},{id: "library-renewable-energy-and-sustainability-report",
          title: 'Renewable Energy and Sustainability Report',
          description: "Renewable Energy and Sustainability Report",
          section: "Library",handler: () => {
              window.location.href = "/library/renewable-energy-sustainability-report/";
            },},{id: "library-biodiversité-en-haute-mer-suspendues-depuis-l-été-2022-les-négociations-rouvrent-pour-un-potentiel-dernier-round",
          title: 'Biodiversité en haute mer : suspendues depuis l’été 2022, les négociations rouvrent pour...',
          description: "Cette session sera-t-elle la dernière ? Suspendues en août dernier, les négociations sur le futur traité juridiquement contraignant visant à conserver...",
          section: "Library",handler: () => {
              window.location.href = "/library/biodiversite-en-haute-mer-suspendues-depuis-lete-2022-les-negociations-rouvrent-pour-un-potentiel-dernier-round/";
            },},{id: "library-traité-sur-la-haute-mer-à-qui-appartiennent-les-ressources-de-l-océan",
          title: 'Traité sur la haute mer : à qui appartiennent les ressources de l’océan...',
          description: "Les États membres de l’ONU reprennent les négociations d’un traité sur la haute mer ce lundi 20 février pour réglementer et mieux protéger les eaux internationales. L’un des principaux points de bloca...",
          section: "Library",handler: () => {
              window.location.href = "/library/traite-sur-la-haute-mer-a-qui-appartiennent-les-ressources-de-locean/";
            },},{id: "library-1st-part-of-the-28th-annual-session-of-the-international-seabed-authority-isa",
          title: '1st Part of the 28th Annual Session of the International Seabed Authority (ISA)...',
          description: "1st Part of the 28th Annual Session of the International Seabed Authority (ISA)",
          section: "Library",handler: () => {
              window.location.href = "/library/1st-part-28th-annual-session-international-seabed-authority-isa/";
            },},{id: "library-el-tratado-de-alta-mar-no-bastará-para-evitar-la-minería-submarina",
          title: 'El Tratado de alta mar no bastará para evitar la minería submarina',
          description: "El experto en política internacional Glen Wright aclara que el Tratado de alta mar de la ONU no podrá por sí solo frenar la minería submarina",
          section: "Library",handler: () => {
              window.location.href = "/library/el-tratado-de-alta-mar-no-bastara-para-evitar-la-mineria-submarina/";
            },},{id: "library-environmental-impact-assessments-on-the-high-seas",
          title: 'Environmental Impact Assessments on the High Seas',
          description: "Environmental Impact Assessments on the High Seas",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-environmental-impact-assessments-high-seas/";
            },},{id: "library-high-seas-treaty-preliminary-analysis-and-implementation-challenges",
          title: 'High Seas Treaty: preliminary analysis and implementation challenges',
          description: "High Seas Treaty: preliminary analysis and implementation challenges",
          section: "Library",handler: () => {
              window.location.href = "/library/high-seas-treaty-preliminary-analysis-implementation-challenges/";
            },},{id: "library-the-inside-story-of-the-u-n-high-seas-treaty",
          title: 'The Inside Story of the U.N. High Seas Treaty',
          description: "The Inside Story of the U.N. High Seas Treaty",
          section: "Library",handler: () => {
              window.location.href = "/library/inside-story-u-n-high-seas-treaty/";
            },},{id: "library-négocié-depuis-2018-à-new-york-l-accord-quot-historique-quot-sur-la-biodiversité-en-haute-mer-est-enfin-acté",
          title: 'Négocié depuis 2018 à New York, l’accord &amp;quot;historique&amp;quot; sur la biodiversité en haute...',
          description: "Après cinq sessions de négociations commencées en 2018, les États ont enfin acté le 4 mars 2023 à New York le futur traité international juridiquement...",
          section: "Library",handler: () => {
              window.location.href = "/library/negocie-depuis-2018-a-new-york-laccord-historique-sur-la-biodiversite-en-haute-mer-est-enfin-acte/";
            },},{id: "library-post-2020-global-biodiversity-framework-what-s-next-for-the-ocean",
          title: 'Post-2020 Global Biodiversity Framework: what’s next for the Ocean?',
          description: "Post-2020 Global Biodiversity Framework: what’s next for the Ocean?",
          section: "Library",handler: () => {
              window.location.href = "/library/post-2020-global-biodiversity-framework-whats-next-ocean/";
            },},{id: "library-non-use-measures-in-international-law",
          title: 'Non-use Measures in International Law',
          description: "Non-use Measures in International Law",
          section: "Library",handler: () => {
              window.location.href = "/library/non-use-measures-international-law/";
            },},{id: "library-much-still-pending-on-how-high-seas-sanctions-will-work",
          title: 'Much still pending on how high seas sanctions will work',
          description: "A new global treaty on the high seas will enable the creation of sanctuaries deemed vital for the oceans, but many questions remain unanswered. Among them: How can we protect marine areas far from the...",
          section: "Library",handler: () => {
              window.location.href = "/library/pending-how-high-seas-sanctions-work/";
            },},{id: "library-further-resumed-fifth-session-of-the-intergovernmental-conference-on-an-international-legally-binding-instrument-under-the-united-nations-convention-on-the-law-of-the-sea-on-the-conservation-and-sustainable-use-of-marine-biological-diversity-of-areas-beyond-national-jurisdiction",
          title: 'Further resumed fifth session of the Intergovernmental conference on an international legally binding...',
          description: "Further resumed fifth session of the Intergovernmental conference on an international legally bindin...",
          section: "Library",handler: () => {
              window.location.href = "/library/resumed-fifth-session-intergovernmental-conference-international-legally-binding-instrument-united-nations-convention-law-sea-conservation-sustainable-use-marine-biological-diversity-areas-beyond/";
            },},{id: "library-workshop-on-supplementary-indicators-towards-climate-targets",
          title: 'Workshop on supplementary indicators towards climate targets',
          description: "Building on recent work by DIW Berlin, Ecologic, and Client Earth, practices established by the UK Climate Change Committee, and global tracking such as the IEA Tracking Clean Energy Progress reports,...",
          section: "Library",handler: () => {
              window.location.href = "/library/workshop-supplementary-indicators-towards-climate-targets/";
            },},{id: "library-global-status-of-renewables",
          title: 'Global Status of Renewables',
          description: "Global Status of Renewables",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-global-status-renewables/";
            },},{id: "library-gwec-gwo-wind-workforce-outlook-webinar",
          title: 'GWEC-GWO Wind Workforce Outlook webinar',
          description: "GWEC-GWO Wind Workforce Outlook webinar",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-gwec-gwo-wind-workforce-outlook-webinar/";
            },},{id: "library-cilmate-change-international-law-amp-negotiations",
          title: 'Cilmate Change: International Law &amp;amp; Negotiations',
          description: "Cilmate Change: International Law &amp; Negotiations",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-cilmate-change-international-law-negotiations/";
            },},{id: "library-renewables-2024-global-status-report-economic-and-social-value-creation",
          title: 'Renewables 2024 Global Status Report: Economic and Social Value Creation',
          description: "Renewables 2024 Global Status Report: Economic and Social Value Creation",
          section: "Library",handler: () => {
              window.location.href = "/library/renewables-2024-global-status-report-economic-social-value-creation/";
            },},{id: "library-renewables-2024-global-status-report-energy-demand",
          title: 'Renewables 2024 Global Status Report: Energy Demand',
          description: "Despite a notable decline in the prices of fossil fuels and other energy commodities in the first half of 2023, wholesale electricity prices remained high in many countries, negatively affecting energ...",
          section: "Library",handler: () => {
              window.location.href = "/library/renewables-2024-global-status-report-energy-demand/";
            },},{id: "library-renewables-2024-global-status-report-energy-supply",
          title: 'Renewables 2024 Global Status Report: Energy Supply',
          description: "Global investment in and deployment of renewables reached an all-time high in 2023, despite high interest rates and higher costs of raw materials. Globally, renewable energy supplied 30% of electric...",
          section: "Library",handler: () => {
              window.location.href = "/library/renewables-2024-global-status-report-energy-supply/";
            },},{id: "library-renewables-2024-global-status-report-energy-systems-and-infrastructure",
          title: 'Renewables 2024 Global Status Report: Energy Systems and Infrastructure',
          description: "This module explores the status and recent trends of some of the building blocks of the energy system, as well as technology advancements that are enabling the integration of higher shares of variable...",
          section: "Library",handler: () => {
              window.location.href = "/library/renewables-2024-global-status-report-energy-systems-infrastructure/";
            },},{id: "library-buildings-and-climate-global-forum",
          title: 'Buildings and Climate Global Forum',
          description: "The Buildings and Climate Global Forum, co-organised by France and the United Nations Environment Programme (UNEP), with the support of the Global Alliance for Buildings and Construction, gathered for...",
          section: "Library",handler: () => {
              window.location.href = "/library/buildings-climate-global-forum/";
            },},{id: "library-how-to-protect-our-ocean",
          title: 'How to Protect Our Ocean',
          description: "How to Protect Our Ocean",
          section: "Library",handler: () => {
              window.location.href = "/library/how-protect-ocean/";
            },},{id: "library-énergies-renouvelables-quot-une-capacité-trop-faible-pour-suivre-l-39-augmentation-de-la-consommation",
          title: 'Énergies renouvelables: &amp;quot;Une capacité trop faible pour suivre l&amp;#39;augmentation de la consommation',
          description: "Énergies renouvelables: &quot;Une capacité trop faible pour suivre l&#39;augmentation de la consommation",
          section: "Library",handler: () => {
              window.location.href = "/library/energies-renouvelables-une-capacite-trop-faible-pour-suivre-laugmentation-de-la-consommation/";
            },},{id: "library-fourteenth-session-of-the-irena-assembly-part-ii",
          title: 'Fourteenth Session of the IRENA Assembly, Part II',
          description: "The Assembly session delved into the crucial theme of “Outcome of COP28: Infrastructure, Policies and Skills for Tripling Renewables and Accelerating the Energy Transition”. Marking the 4th World Ener...",
          section: "Library",handler: () => {
              window.location.href = "/library/fourteenth-session-irena-assembly-part-ii/";
            },},{id: "library-the-future-of-energy-new-technologies-and-human-development",
          title: 'The Future of Energy: New Technologies and Human Development',
          description: "The Future of Energy: New Technologies and Human Development",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-future-energy-new-technologies-human-development/";
            },},{id: "library-renewables-2024-global-status-report-global-overview",
          title: 'Renewables 2024 Global Status Report, Global Overview',
          description: "Policy responses to geopolitical developments and global commitments accelerated the deployment and use of renewable energy in 2023, especially in the power sector. The historic decision at the 2023...",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-renewables-2024-global-status-report-global-overview/";
            },},{id: "library-renewables-2025-global-status-report-global-overview",
          title: 'Renewables 2025 Global Status Report: Global Overview',
          description: "In 2024, global renewable energy growth was primarily driven by the power sector, where capacity expanded by 741 gigawatts (GW), the largest annual increase ever recorded. Solar photovoltaics (PV) led...",
          section: "Library",handler: () => {
              window.location.href = "/library/renewables-2025-global-status-report-global-overview/";
            },},{id: "library-global-alliance-for-buildings-and-construction-globalabc-general-assembly",
          title: 'Global Alliance for Buildings and Construction (GlobalABC) General Assembly',
          description: "Since the 2023 GlobalABC Annual Assembly in Helsinki (1 and 2 June 2023), GlobalABC has been highly active, strengthening its role as a community and a collaborative force for a zero-emission, resilie...",
          section: "Library",handler: () => {
              window.location.href = "/library/global-alliance-buildings-construction-globalabc-general-assembly/";
            },},{id: "library-governing-marine-spaces-in-the-context-of-the-energy-transitions-challenges-and-cooperation",
          title: 'Governing marine spaces in the context of the energy transitions: challenges and cooperation...',
          description: "Governing marine spaces in the context of the energy transitions: challenges and cooperation",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-governing-marine-spaces-context-energy-transitions-challenges-cooperation/";
            },},{id: "library-renewables-for-nature-integrating-biodiversity-amp-communities-in-energy-policy",
          title: 'Renewables for Nature: Integrating Biodiversity &amp;amp; Communities in Energy Policy',
          description: "How can renewable energy accelerate the energy transition while also delivering tangible benefits for nature and communities? This joint online event hosted by The Nature Conservancy (TNC) and REN21...",
          section: "Library",handler: () => {
              window.location.href = "/library/renewables-nature-integrating-biodiversity-communities-energy-policy/";
            },},{id: "library-à-new-york-une-cérémonie-acte-l-entrée-en-vigueur-début-2026-du-traité-sur-la-biodiversité-en-haute-mer",
          title: 'À New York, une cérémonie acte l’entrée en vigueur début 2026 du traité...',
          description: "Les représentants des 68 États ayant à ce jour ratifié le traité sur la préservation et l’utilisation durable de la biodiversité en haute mer se sont réunis le 23 septembre 2025 à New York, en marge d...",
          section: "Library",handler: () => {
              window.location.href = "/library/a-new-york-une-ceremonie-acte-lentree-en-vigueur-debut-2026-du-traite-sur-la-biodiversite-en-haute-mer/";
            },},{id: "library-renewables-in-energy-supply-ocean-power",
          title: 'Renewables in Energy Supply: Ocean Power',
          description: "Renewables in Energy Supply: Ocean Power",
          section: "Library",handler: () => {
              window.location.href = "/library/glen-wright-renewables-energy-supply-ocean-power/";
            },},{id: "library-le-traité-sur-la-protection-de-la-biodiversité-en-haute-mer-entre-en-vigueur",
          title: 'Le traité sur la protection de la biodiversité en haute mer entre en...',
          description: "Le traité sur la protection de la biodiversité en haute mer entre en vigueur",
          section: "Library",handler: () => {
              window.location.href = "/library/le-traite-sur-la-protection-de-la-biodiversite-en-haute-mer-entre-en-vigueur/";
            },},{id: "library-foro-social-más-allá-del-crecimiento",
          title: 'Foro Social Más Allá del Crecimiento',
          description: "Un espacio de encuentro para construir democráticamente las bases de una transición ecosocial justa que cuestione el capitalismo verde y proponga alternativas más allá del crecimiento basadas en el de...",
          section: "Library",handler: () => {
              window.location.href = "/library/foro-social-mas-alla-del-crecimiento/";
            },},{id: "library-presentació-la-guerra-por-la-energía-d-alberto-garzón",
          title: 'Presentació: La guerra por la energía, d´Alberto Garzón',
          description: "En La guerra por la energía, el exministro Alberto Garzón recorre la historia de la humanidad desde los cazadores-recolectores de la prehistoria hasta el capitalismo del siglo XXI, pasando por el colo...",
          section: "Library",handler: () => {
              window.location.href = "/library/presentacio-la-guerra-por-la-energia-d-alberto-garzon/";
            },},{id: "projects-academia-obscura",
          title: 'Academia Obscura',
          description: "The hidden silly side of higher education",
          section: "Projects",handler: () => {
              window.location.href = "/projects/academia_obscura/";
            },},{id: "projects-crossword",
          title: 'crossword',
          description: "Get a crossword published by the New York Times",
          section: "Projects",handler: () => {
              window.location.href = "/projects/crossword/";
            },},{id: "projects-folk-directory",
          title: 'Folk Directory',
          description: "A user-maintained listing of UK folk clubs and sessions.",
          section: "Projects",handler: () => {
              window.location.href = "/projects/folk_directory/";
            },},{id: "projects-hoops",
          title: 'Hoops',
          description: "An Uncommon Field Guide to the Game of Basketball",
          section: "Projects",handler: () => {
              window.location.href = "/projects/hoops/";
            },},{id: "projects-little-blue-letter",
          title: 'Little Blue Letter',
          description: "A splash of uplifting ocean stuff, lovingly curated by young ocean leaders",
          section: "Projects",handler: () => {
              window.location.href = "/projects/little_blue_letter/";
            },},{id: "projects-marine-policy-amp-ocean-governance",
          title: 'Marine Policy &amp;amp; Ocean Governance',
          description: "A master&#39;s course exploring the political, legal and institutional frameworks governing the ocean.",
          section: "Projects",handler: () => {
              window.location.href = "/projects/marine-policy-ocean-governance/";
            },},{id: "projects-marine-regions-forum",
          title: 'Marine Regions Forum',
          description: "Achieving a Healthy Ocean – Regional Ocean Governance Beyond 2020",
          section: "Projects",handler: () => {
              window.location.href = "/projects/marine_regions_forum/";
            },},{id: "projects-post-employment",
          title: 'Post-employment',
          description: "I want my last job to be my last job",
          section: "Projects",handler: () => {
              window.location.href = "/projects/post_employment/";
            },},{id: "projects-ren21-knowledge-amp-data-rethink",
          title: 'REN21 Knowledge &amp;amp; Data Rethink',
          description: "Overhauling REN21&#39;s renewable energy reporting, data infrastructure and production processes",
          section: "Projects",handler: () => {
              window.location.href = "/projects/ren21_rethink/";
            },},{id: "projects-renewables-global-status-report",
          title: 'Renewables Global Status Report',
          description: "The world’s leading annual assessment of renewable energy progress",
          section: "Projects",handler: () => {
              window.location.href = "/projects/renewables_global_status_report/";
            },},{id: "projects-renweb",
          title: 'RENWEB',
          description: "A comprehensive platform for REN21&#39;s renewable energy and policy data",
          section: "Projects",handler: () => {
              window.location.href = "/projects/renweb/";
            },},{id: "projects-strong-high-seas",
          title: 'STRONG High Seas',
          description: "Strengthening Regional Ocean Governance for Areas Beyond National Jurisdiction",
          section: "Projects",handler: () => {
              window.location.href = "/projects/strong_high_seas/";
            },},{id: "projects-transcriptx",
          title: 'TranscriptX',
          description: "A place to think with transcripts",
          section: "Projects",handler: () => {
              window.location.href = "/projects/transcriptx/";
            },},{id: "projects-website",
          title: 'website',
          description: "Building an online homespace",
          section: "Projects",handler: () => {
              window.location.href = "/projects/website/";
            },},{id: "services-applied-ai-amp-workflow-design",
          title: 'Applied AI &amp;amp; Workflow Design',
          description: "Help NGOs, research groups, and small teams make practical, ethical use of AI and lightweight digital tools in their everyday work.",
          section: "Services",handler: () => {
              window.location.href = "/services/applied-ai-workflow-design/";
            },},{id: "services-coaching-amp-career-support",
          title: 'Coaching &amp;amp; Career Support',
          description: "One-to-one coaching for students, early-career professionals, and mid-career practitioners working in oceans, energy, climate, and adjacent fields.",
          section: "Services",handler: () => {
              window.location.href = "/services/coaching-career-support/";
            },},{id: "services-copyediting-amp-proofing",
          title: 'Copyediting &amp;amp; Proofing',
          description: "Copyediting and proofing services for reports, academic articles, policy briefs, funding proposals, and other written outputs.",
          section: "Services",handler: () => {
              window.location.href = "/services/copyediting-proofing/";
            },},{id: "services-energy-transition-amp-renewables",
          title: 'Energy Transition &amp;amp; Renewables',
          description: "Support for organisations working on renewable energy and energy systems to interpret global trends and apply them to their specific context.",
          section: "Services",handler: () => {
              window.location.href = "/services/energy-transition-renewables/";
            },},{id: "services-ocean-amp-marine-policy",
          title: 'Ocean &amp;amp; Marine Policy',
          description: "Strategic advice on international ocean governance, with a particular focus on the high seas, seabed mining, and regional cooperation.",
          section: "Services",handler: () => {
              window.location.href = "/services/ocean-marine-policy/";
            },},{id: "services-orientation-sessions",
          title: 'Orientation Sessions',
          description: "Design and facilitation of workshops, retreats, and learning journeys for teams working on oceans, energy, and climate.",
          section: "Services",handler: () => {
              window.location.href = "/services/orientation-sessions/";
            },},{id: "services-workshops-facilitation-amp-learning-design",
          title: 'Workshops, Facilitation &amp;amp; Learning Design',
          description: "Design and facilitation of workshops, retreats, and learning journeys for teams working on oceans, energy, and climate.",
          section: "Services",handler: () => {
              window.location.href = "/services/workshops-facilitation-learning/";
            },},{id: "teaching-marine-policy-amp-ocean-governance",
          title: 'Marine Policy &amp;amp; Ocean Governance',
          description: "A graduate seminar exploring the political, legal and institutional frameworks governing the ocean. Students examine global and regional governance regimes, with case studies on biodiversity, fisheries, and emerging issues like deep sea mining and ocean energy.",
          section: "Teaching",handler: () => {
              window.location.href = "/teaching/marine-policy/";
            },},{id: "teaching-anthropocene-book-club",
          title: 'Anthropocene Book Club',
          description: "A graduate seminar exploring the political, legal and institutional frameworks governing the ocean. Students examine global and regional governance regimes, with case studies on biodiversity, fisheries, and emerging issues like deep sea mining and ocean energy.",
          section: "Teaching",handler: () => {
              window.location.href = "/teaching/anthropocene-book-club/";
            },},{
        id: 'social-email',
        title: 'email',
        section: 'Socials',
        handler: () => {
          window.open("mailto:%67%6C%65%6E.%77.%77%72%69%67%68%74@%67%6D%61%69%6C.%63%6F%6D", "_blank");
        },
      },{
        id: 'social-github',
        title: 'GitHub',
        section: 'Socials',
        handler: () => {
          window.open("https://github.com/glen-w", "_blank");
        },
      },{
        id: 'social-linkedin',
        title: 'LinkedIn',
        section: 'Socials',
        handler: () => {
          window.open("https://www.linkedin.com/in/glen-wright-49455428", "_blank");
        },
      },{
        id: 'social-orcid',
        title: 'ORCID',
        section: 'Socials',
        handler: () => {
          window.open("https://orcid.org/0000-0002-9162-9618", "_blank");
        },
      },{
        id: 'social-researchgate',
        title: 'ResearchGate',
        section: 'Socials',
        handler: () => {
          window.open("https://www.researchgate.net/profile/https://www.researchgate.net/profile/Glen-Wright# your profile on ResearchGate/", "_blank");
        },
      },{
        id: 'social-scholar',
        title: 'Google Scholar',
        section: 'Socials',
        handler: () => {
          window.open("https://scholar.google.com/citations?user=QHaIr0sAAAAJ", "_blank");
        },
      },];
