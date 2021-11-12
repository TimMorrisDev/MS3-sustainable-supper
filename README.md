# Sustainable Supper Club
___
![Responsive Mockup of site]()


# Project Synopsis

'The Sustainable Supper Club'. A website dedicated to providing users with great vegetarian and vegan recipes based on what they have left over in their pantry. The goal is to open the door for people to live more sustainably and get inspiration for ways to eat less meat and waste less food.


[See the live site here!](https://sustainable-supper-club.herokuapp.com/)

___
# User Experience (UX)

## User Stories

### First time user goals
- I want to find delicious recipes to make.
- I want to search for recipes I can make with the ingredients I already have.
- I'm interested in cooking more vegetarian or vegan food but don't know where to start.
- I want to sign up to get more features easily.

### Returning user goals

- I want to save a list of my favourite recipes.
- I want to be able to easily view recipes that match the ingredients I have left in my kitchen.
- I want to add my own recipes for the community to enjoy.

### Frequent user goals

- I want to see what the community is eating by seeing the top recipes being made.

### Business Goals

- To promote more sustainable eating habits.
- To allow users to find delicious and healthy food to cook.
- To track what people are most enjoying cooking to help future development / customer engagement strategies.

## Design

### Colour Scheme

    I wanted to carry across the themes of sustainability and natural eating / living so I sourced the following image of a lushous landscape extracted my colour palette from that.

    ![landscape photo for colour palette](/workspace/MS3-sustainable-supper-club/static/readme_assets/ux/colour_palette/landscape.jpeg)

    Below is the resulting palette generated using the [Coloors.co](https://coolors.co/) 'generate from image' tool.

    ![colour palette generated from image](/workspace/MS3-sustainable-supper-club/static/readme_assets/ux/colour_palette/MS3-Palette.pdf)

### Fonts
    - Montserrat / Roboto.

        I used Montserrat for most of the site content but kept Roboto on hand for more space-sensitive needs as it is slightly more compact in its width.

### Wireframes
    - [Landing / Game Page](https://github.com/TimMorrisDev/MS2-song-remixer/blob/main/assets/ux/wireframes/Home.pdf)

    - [Contact Us](https://github.com/TimMorrisDev/MS2-song-remixer/blob/main/assets/ux/wireframes/contact.pdf)

### Design Decisions Different to Wireframes
   
## Features

- Browse all recipes.
- Sign up to create personal profile.
- Save favourite recipes to profile.
- Search recipes by ingredients a user has in their kitchen.
- Get inspiration for new recipes using the top 3.


### Other Features
- Responsive across all devices and screen sizes.
- Adaptive to modify content shown to be appropriate for user device or screen size.

### Future Development Opportunities

___
# Technologies Used
## Languages Used
- [Python3](https://www.python.org/downloads/)
- [JavaScript](https://www.javascript.com/)
- [CSS3](https://en.wikipedia.org/wiki/CSS)
- [HTML5](https://en.wikipedia.org/wiki/HTML5)


## Frameworks, Libraries & Programs Used

- [jQuery](https://jquery.com/)
    - I used jQuery in my Javascript code for the song remixer game. I mostly made use of event handlers to integrate user interaction with the site with my Javascript functions controlling the features offered to the user.
    - jQuery was also used as part of Bootstrap and is used for Javascript plugins such as the responsive nav bar and modals.

- [Bootstrap](https://getbootstrap.com/docs/4.5/getting-started/introduction/)
    - Bootstrap was used for the responsive 'grid'. Code snippets from the Bootstrap documentation were used in various places and modified to suit the purpose and design of the site.
- [EmailJS](https://www.emailjs.com/)
    - 
- [Google Fonts](https://fonts.google.com/)
    - Google Fonts was used to import the 'Montserrat', and 'Tourney' fonts, which were used throughout the site.
- [Font Awesome](https://fontawesome.com/)
    - Used to source images for the transport section of the remixer.

- [Git](https://git-scm.com/)
    - Git was used for version control using the terminal in Gitpod to 'add' and 'commit' to Git and to push changes to the GitHub repository using 'git push'.

- [Gitpod](https://gitpod.io/)
    - Gitpod.io was used as the primary development environment when coding for the site. It's terminal was used to preview the site via temporary server, and for version control using Git commands.
- [Github](https://github.com/)
    - GitHub was used to store the code pushed from Gitpod and as deployment for the [published site.](https://timmorrisdev.github.io/MS2-song-remixer/)
- [Balsamiq](https://balsamiq.com/)
    - Balsamiq was used to create the wireframes for the site while in the 'skeleton' stage of my UX process.
- [Autoprefixer](http://autoprefixer.github.io/)
    - Autoprefixer was used in the final stage of development to parse CSS code and add vendor prefixes.
- [Coloors.co](https://coolors.co/)
    - Used to source colour palettes used throughout the site.
- [CSS Gradient](https://cssgradient.io/)
    - Used to generate background radial gradient effects.
- [Am I Responsive?](http://ami.responsivedesign.is/#)
    - Used to check responsiveness across different device sizes. 

___
# Testing
## Responsiveness Testing
I used google dev tools throughout the development process to check responsiveness across different screen sizes. 

I was also sure to deploy the site to GitHub pages early in development to allow for review of the live site on various devices throughout the process.

## W3C Markup, CSS Validation & JSHint Validation
I used the W3C Markup, CSS Validator and JSHint Validator Services to check and validate each page throughout the site to check for errors. 
### [Markup Validation Service](https://validator.w3.org/)
The validator found the following issues for me to address.
- Element hr not allowed as child of element ol in this context.
    - This was due to my nesting of hr elements within my game-instruction modal unordered list. I modified my code to include 'border-bottom' styling for each list item to rectify the issue.

### [CSS Validation Service](https://jigsaw.w3.org/css-validator/)
My CSS file style.css passed through the w3 validator with no errors.

### [JSHint Validation Service](https://jshint.com/)
The validator found the following warnings for me to address. 
- 'Function declarations should not be placed in blocks. Use a function expression or move the statement to the top of the outer function.'
    - This was caused by my addition of a setTimeout function to the buildPads function to allow for the 'cascading' effect while the pads are populating the game area. I had not removed the original function from within the setTimeout, which was now not needed. 
    - Whilst this issue was fixed there is still a warning stating: 
    
        "Functions declared within loops referencing an outer scoped variable may lead to confusing semantics. (currentSongId, i)"

        As I am using the reference outer scoped variables to apply styles and parameters based on the song selected, it is my understanding that this warning can be ignored for the purpose of this site.
- One undefined variable - Howl.
    - This is in fact not a variable but a reference to the 'Howl' class constructor used by HowlerJS. It is my understanding that the validator does not recognise the external, HowlerJS library being used and therefore I can ignore this warning for the purpose of this site.
- One unused variable - stopBtn.
    - At the top of my code, I have declared variables for various DOM elements I was likely to need to reference throughout the project. I had not needed to reference stopBtn and therefore it needed to be removed to pass validation.

## Lighthouse Testing
Lighthouse testing on the main website game page found the following issues.
- 'Links do not have a discernible name'.
    - I am using icons in my footer links and therefore had no text to act as description. This was solved by adding the 'aria-label' attribute to each anchor tag with a short description. 

- Heading elements are not in a sequentially-descending order (contact.html).
    - This is a minor issue that I chose to ignore for the purpose of the site.

Once this issue was resolved, lighthouse testing returned the following results:

Main game page.

![main page lighthouse](assets/ux/screengrabs/main-page-lighthouse.png)

Contact page.

![contact page lighthouse](assets/ux/screengrabs/contact-lighthouse.png)

## Testing UX User Stories

- I want to easily understand the game and how to play.
    - There are clear and simple instructions presented on the landing page. 
    ![main-instructions](assets/ux/screengrabs/main-instructions.png)
    There is also the option to reveal more detailed game instructions if required by hitting the info button in the transport bar of the main game page. 
    ![expanded instruction screengrab](assets/ux/screengrabs/expanded-instructions.png)

- I want to remix different songs by bringing elements of the track in and out.
    - By using the clearly-labelled pads on the main game page. I was able to manipulate which instruments were being heard in the mix of the song. It was easy to see which instruments were not being heard as the pad became 'greyed-out' when that instrument was muted.
    ![pad view](assets/ux/screengrabs/pad-view.png)

- The site should be visually appealing and well laid out, with different colour themes for each song.
    - The game area is clearly modified for each song with defined themes that suit the bands image. There are also 'light' and 'dark' mode toggles so that the user can further customise their experience. 

    ![aloosh light mode](assets/ux/screengrabs/aloosh-light.png)

    ![aloosh dark mode](assets/ux/screengrabs/aloosh-dark.png)
    
    ![escape light mode](assets/ux/screengrabs/escape-light.png)

    ![escape dark mode](assets/ux/screengrabs/escape-dark.png)

- I want to discover the music of the band Volleyball.
    - The game offers two different songs for the user to explore and play with. The starting state is for all pads to heard and therefore giving the user the full experience of the song before exploring.

    ![songs screengrab](assets/ux/screengrabs/songs.png)

- I want to be able to connect with the band featured on their social media, and find out more about them on their own website.
    - Link to the bands social media pages, as well as their website were clear and easy to find in the footer of the page. The section on the home page clearly explained that Volleyball is the band featured and their logo links to their website.

    ![band info screengrab](assets/ux/screengrabs/band-info.png)
    ![footer links](assets/ux/screengrabs/page-footer.png)

## Testing Business Goals

More data would need to be collected on an ongoing basis to establish the success of the business goals relating to driving traffic to social media pages or increasing exposure of new song releases. 

My user feedback and peer-review so far at least tells me that I have created a game that is fun and engaging to play, which allows the user to experience the bands music in a new and exciting way.

## Peer Code Review

I submitted this project to the 'peer-code-review' Slack channel on Monday 11th August to collect user feedback. 

I received several positive reactions to the site but did not get any comments to highlight any issues or negative user experience. I will leave the site active on this channel and collect any data for possible future development.

## Cross-Browser/Device Testing
I tested the site across multiple devices using different browsers.
- Browsers tested
    - Chrome
    - Safari
    - Firefox

- Devices tested
    - Mac Pro w/ Dell 24 inch monitor
    - Macbook Pro 15 inch
    - iPhone 12
    - iPad air 2

## Known Bugs / Issues
- 'The AudioContext was not allowed to start. It must be resumed (or created) after a user gesture on the page (howler.core.min.js:2)'
    - This issue is being shown as a warning in the google dev tools console. After researching the issue, I found that even though I am not implementing any auto-play of audio on the site, the library HowlerJS is initialising audio contexts as part of its code. This is recognised as a play event by google dev tools even though it is not actually beginning playback of any audio. I found several posts on Stack Overflow where people had experienced the same warnings and it appears to be an error on google's side. 
    I found [this Stack Overflow article](https://stackoverflow.com/questions/66801354/web-audio-api-the-audiocontext-was-not-allowed-to-start-it-must-be-resumed-o) where people were experiencing the same issue.

    ![Article screengrab](assets/ux/screengrabs/bug-answer-screengrab.png)
___
# Deployment
## GitHub Pages
The project was deployed to GitHub pages using the following method. 
1. Log in to [GitHub.com](https://github.com/) and locate the [MS2-song-remixer repository](https://github.com/TimMorrisDev/MS2-song-remixer) in my account.
2. Select the repo 'settings' menu and navigate to the 'pages' tab on the left hand side.
3. In the 'source' section, select the master branch as the source for the site deployment. 
4. Hit 'save' and wait a few minutes for GitHub to process. The 'pages' settings tab will now show a message to confirm the repository is being published to the address https://timmorrisdev.github.io/MS2-song-remixer/.

## Forking the repository in GitHub
Forking the repository creates a copy of the original repository in your own account to allow changes to be made without affecting the original repository.
1. Log in to GitHub and navigate to the GitHub repository page [here](https://github.com/TimMorrisDev/MS2-song-remixer).
2. In the top-right of the page, below the user avatar, locate the "fork" button.
3. Click the "fork" button and you should now have a copy of the repository in your own account. 

## Making a Local Clone
Details of how to make a local copy of the GutHub repository can be found [here](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository). To clone using HTTPS follow these steps.
1. Navigate to the GitHub repository [here](https://github.com/TimMorrisDev/MS2-song-remixer).
2. Click the "Code" drop-down menu above the list of files.
3. Copy the HTTPS address to the clipboard using the button provided.
4. Open Terminal.
5. Change the current directory to the location you wish to copy the directory.
6. Type 'git clone' and then paste the HTTPS url you copied earlier. 
7. Press enter and your local clone will be created. 

___
# Credits
## Code
- Inspiration for player features and layout from [Traversy Media](https://www.youtube.com/watch?v=QTHRWGn_sJw) and [Junior Developer Central](https://www.youtube.com/watch?v=jZL9gVwxO-U) YouTube videos.
- Responsive grid for pads taken from [Stack Overflow article](https://stackoverflow.com/questions/46548987/a-grid-layout-with-responsive-squares) and modified to suit the site needs.
- General information about class constructors and class inheritance from [The Net Ninja 'object oriented JavaScript'](https://www.youtube.com/watch?v=4l3bTDlT6ZI&list=PL4cUxeGkcC9i5yvDkJgt60vNVWffpblB7) YouTube series.
- Information relating to [HowlerJS](https://howlerjs.com/) gathered from [Techlahoma YouTube video](https://www.youtube.com/watch?v=isCQptdu1Kg).
- Code for audio 'Howls' copied from [HowlerJS](https://howlerjs.com/) documentation ['AudioSprite' demo](https://github.com/goldfire/howler.js#documentation) and then edited to fit the needs of the site. 
- [Stack Overflow](https://stackoverflow.com/), [w3 Schools](https://www.w3schools.com/) & [CSS tricks](https://css-tricks.com/) were used throughout the project to research solutions to site requirements.


## Content
- All content written by the developer.

## Media
- All music written by, and copyright of the band Volleyball.

## Acknowledgements
- Thank ypu to my mentor, Can Sucullu for all your guidance and support.
- Thank you to Volleyball for agreeing to share their music for the purpose of this project.
