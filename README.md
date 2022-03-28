

<p align='center'>
    <img src='https://github.com/macglencoe/Schoology-Pro/blob/main/logo.png' alt='Logo'/>
</p>
<h2 align="center">Schoology Pro</h3>
<h4 align="center">(ScPro)</h4>

## Table of Contents
- [About The Project](#about-the-project)
    - [Built With](#built-with)
- [Getting Started](#getting-started)
    - [Authorization with OAuth](#authorization-with-oauth)
- [Bugs and Feature Requests](#bugs-and-feature-requests)

## About The Project
Schoology is a web-based service responsible for accepting, calculating, storing, and displaying student grades. Although it is used by many schools, the interface and style of grade representation is far from intuitive.

This project seeks to provide up-to-date grade representation and necessary features for students who want to **see** the potential in their grades.

While Schoology only represents grades in plain text, ScPro will provide *visual* representation - such as charts and graphs which visualize the weights of assignments, categories, and sections.

A well-anticipated feature will be the interactivity of the shown results. A student deserves to know what their grade would look like, were they to re-do an assignment, drop a grade, etc., without needing to calculate it themselves.

### Built With
* [Streamlit](https://streamlit.io)
> Serves as the hosting and GUI framework, crucial for making this web-app possible.
* [schoolopy](https://github.com/ErikBoesen/schoolopy)
> Made by [Erik Boesen](https://github.com/ErikBoesen), an extremely helpful Python wrapper for Schoology's API.
* [altair](http://altair-viz.github.io)
> Used to create the graphs and charts in ScPro.

## Getting Started
ScPro is a fully online webapp. All you need to do in order to use the app is go to the site, hosted by Streamlit.

ScPro uses cookies to save your session-state, so you don't have to authorize and load your data every time you use the app.

### Authorization with OAuth
To use this app, you need to authorize the app with schoology using a unique link, provided in-app.

- Click 'Login with Schoology' and a tab will open with your district's (BCS's) Schoology site, where you can log in securely.

- After you've logged in, Schoology will display a dialog, asking if you would like to authorize the app.

- Click 'Allow' to authorize ScPro. You'll be redirected to your Schoology Homepage, but you can now return to the tab with ScPro, where it should be displaying a 'Logging in' spinner, instead of 'Authorizing'. Please allow at least 5 seconds for the Authorization response to be received.

**This is the safest method for authorization, as it is Schoology's built-in method for app integration.**

**None of your credentials can be accessed by this application.**

**For more info on how Schoology keeps your credentials safe, check out [Schoology's API Docs on Authentication](https://developers.schoology.com/api-documentation/authentication)**

## Bugs and Feature requests
Encountered an error or a bug? Have an idea for a future feature? Here's how you can let me know:
- Submit an issue on GitHub [here](https://github.com/macglencoe/Schoology-Streamlit/issues)
- Contact me personally at [macglencoe3d@gmail.com](mailto:macglencoe3d@gmail.com)

If you have a bug, and it involved an exception (red error message), please include a screenshot or text copy of the message

$$example\:equation$$