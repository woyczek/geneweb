To install Algolia based search:

in /etc/hosts add the entry
127.0.0.1 localweb.fr

In My-params fill-in PASSWD (name:pwd) APPIP and APIKEY 
Executing Make-algolia will update algolia_search.js with the correct appId and apiKey values.
After installing a new distribution (make distrib), you should run again My-params
to obtain your own version of algolia_search.js and algolia/perso.txt.

You may adapt the various attributes in the perso.txt and algolia_search.txt

You need to be able to run a python3 program

Run Make-algolia.command after adjusting the various parameters
SIZE is the number of persons in your base as reported by GeneWeb in the welcome page

Running Make-algolia will produce a file names basename-chunk.json that you may upload
in your Algolia index. Algolia offers a 15 days free trial environment.
Visit algolia.com for details.

In basename.gwf, add the parameter
algolia_search=yes
A new search button will appear in the welcome page (below advanced search) and on each individual page (below search).

