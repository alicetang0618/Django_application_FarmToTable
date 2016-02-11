# Django_application_FarmToTable
An Online trading platform for farmers and urban customers.

Requirement:
	Python, SQLite3, Django
	
Python Packages Required
  - NLTK, NLTK data must be installed
  - Django security session must be installed
  - Scipy

Launch The Program
  - Enter the Farmtotable directory. Run “python manage.py runserver” to start exploring.
  - For error message “That port is already in use”, run “sudo fuser –k 8000/tcp” and rerun the server

Two Ways To Navigate Through Our Site!!!

- The Lone Wolf:
  - Move the db.sqlite3 to a separate directory, delete all files in applications/migrations, run “python manage.py syncdb” to create a new empty database.
  - Start exploring our website with an empty back-end database 
  - Register your own users as buyers or sellers and try out the different functionalities.

- In A Crowd:
  - Fixture file contains the testing data and they are preloaded into db.sqlite3. Move it to the directory to interact with it.
  - The data should be pre-loaded. In case it is not loaded properly, go to farmtotable directory and run “python manage.py loaddata userprofile_fixture.json > applications.userprofile”
  Fixtures to load for all the models include:
  userprofile, product, order, search, rating, donation, item, cart 
  If cannot load one, try load the others first because some objects need to exist for the others to be created.
  - The test data is randomly generated and the relations between objects might not be orderly, so we strongly suggest you to use the empty version for a better sense of how our functions work. 

Site Overview
	Total number of templates:  42
	Technologies used: JavaScript, Html, CSS

Functionalities 
- User: Register, log in, log out, modify profile, upload files. Search, message, like product, shop, checkout and more.
    - Seller:
      - Register product
      - Modify product
      - Cannot leave comments 
      - No product will be recommended for seller
    - Buyer:
      - Being recommended product
      - Leave comments
      
Special Features

Session security
  - Automatically logged out after 10 minutes.
  - Automatically logged out after closing browser

Search
  - User, buyer and guests can search
  - Search history will be stored in the search model:
	  - For registered users it will store the user’s profile, search term, product origin, product category and time. 
  - NLTK:
	  - Search term is case-insensitive, order-insensitive, singular or plural insensitive
	  - Can type in multiple words
	  - Adjectives and nouns are interpreted through NLTK for more accurate search
  - Search in index rather than making direct query to the database. Index is automatically updated each time a product is added. 
  - Search for key words in both product names and descriptions: product whose names contain the key term will appear first. 

Recommendation
- Sources of data:
  - 	User liked product
  - 	User order history
  - 	User rating
- Two-way recommendation:
  Algorithm:
  - 	Calculate the Pearson coefficient as the indicator for similarity
  - 	Arrays supplied: 
  - 	index = product.id – 1; 
  - 	value = average rating of a product or times the user bought this product
- Filter by user
  - 	Recommend high rated product bought by similar users 

- Filter by product
  - 	Find your liked and highly rated product you bought
  - 	Recommend similar product  

Rating & Comments
 - 	Buyers can rate user and product
 - 	Buyers can only rate a product after he or she places an order

Message
	Buyers and sellers can exchange messages.  Go to their profile pages.

Shopping cart, Check out & Payment
	Currently users have their accounts registered with our website. 
  Upon checkout, they could choose to pay differently: online, offline or on delivery. Orders will be received and confirmed by the seller or be canceled by either party. Seller can charge extra delivery fee. 

My Finance
	Monitor your spending in the last three months and view by category.

Further Features To Explore
	Internationalization
	Balance between traffic and capacity
