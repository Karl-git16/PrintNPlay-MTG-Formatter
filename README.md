# PrintNPlay-MTG-Formatter
Card Formatter for Print &amp; Play Games for Proxies

# Requirements
- Have photoshop
- Have the Card images from MPCFILL
- Have the decklist from MPCFILL
- download your webdriver(application currently only works with chrome)

# How to Use Without Application
1. download all the files and go to directory
2. download dependencies using requirements.txt
<pre><code>pip install -r requirements.txt</code></pre>
3. run
<pre><code>pip python main.py</code></pre>

# How to Use With Application
1. make folder, call it whatever
2. download main.exe
4. place main.exe in folder
5. run application

# Run Through of Program
1. you'll be prompted between automatic and manual
  - manual: just needs decklist
  - automatic: needs decklist and card files from MPCFILL(delete cardback file)
2. input what is prompted(decklist and card files)
3. press start processing
  - Creates files and folders
  = Opens photoshop and makes sheets
5. input user and pass of Print & Play Games
  - will open a browser and automatically place order for you and add to cart
6. Exit program

