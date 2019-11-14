# d2ldl 

If you're like me, tired of using this bloated website and you only really need files that were uploaded, feel free to use my script: `d2ldl`. 

The script interactively asks for your login details, displays your current courses, and allows you to download all the files from that course. 

It's pretty barebones. Testing is nonexistent. The web scraping is bound to break at any update on D2L's end. All around, pretty shit but it'll do the job (for now). 

## Requirements

`python3.7` because I like those `f`-strings. 

`beautifulSoup4` for navigating the DOM

`requests-html` for requests. Could have used barebones `requests` because I didn't end up needing the JS rendering functionality, but oh well. 


## Demo 

![](demo.gif)
