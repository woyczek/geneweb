To install Algolia based search:

in /etc/hosts add the entry
127.0.0.1 localweb.fr

Executing Make-algolia will update etc/algolia/perso.txt with the value necessary
to rebuild an index.

You may adapt the various attributes in the perso.txt and algolia_search.txt

You need to be able to run a python3 program

SIZE is the number of persons in your base as reported by GeneWeb in the welcome page

Running Make-algolia will produce two files named basename_public-chunk.json and 
basename_private-chunk.jsonthat you may upload in your Algolia index.
One index should be names "basename_public", the other one should be named "basename"
Algolia offers a 15 days free trial environment.
Visit algolia.com for details.

In basename.gwf, add the parameters
algolia_search=yes
algolia_appid=GMGXXXXIT8M
visitors_apikey=4d0a47ded44xxxxx426a23eb27
friends_apikey4d0a47ded447xxxxxxx426a23eb27

The appropriate values for these parameters will be made available later.

A new search button will appear in the welcome page (below advanced search) and on each individual page (below search).

