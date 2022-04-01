
<p align='center'>
    <img src='https://github.com/macglencoe/Schoology-Pro/blob/main/logo.png' alt='Logo'/>
</p>
<h2 align="center">Schoology Pro</h3>
<h4 align="center">(ScPro)</h4>

## Table of Contents
- [About The Project](#about-the-project)
    - [Built With](#built-with)
    - [Grade Calculation Methods: An Explanation](#grade-calculation-methods-an-explanation)
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

### Grade Calculation Methods: An Explanation
Instructors and admins on Schoology have the ability to choose how their course categories are calculated.

There are two methods for individual-assigment grading:

**Point Average:**

<img src='https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D%5Cfg%7Bwhite%7D%5Cfrac%7Btotal%5C:of%5C:earned%5C:points%7D%7Btotal%5C:of%5C:max%5C:points%7D=grade%5Ctimes100=grade%25' alt='Point Average Formula'/>

*Example: A student has the following graded assignments in a Point Average category:*

| Assignment Name | Earned Points | Max Points
|---|:---:|:---:|
| Assignment 1 | 60 | 100 |
| Assignment 2 | 10 | 10 |
| **Total**| **70** | **110** |

<img src='https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D%5Cfg%7Bwhite%7D%5Cfrac%7B70%7D%7B110%7D=0.6363%5Ctimes100=63.63%25' alt='Point Average Example'/>

---
**Percent Average:**

<img src='https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D%5Cfg%7Bwhite%7D%5Cfrac%7Bsum%5C:of%5C:decimal%5C:scores%7D%7Bcount%5C:of%5C:grades%7D=grade%5Ctimes100=grade%25' alt='Percent Average Formula'/>

*Example: A student has the following graded assignments in a Percent Average category*


<img src='https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D%5Cfg%7Bwhite%7DDecimal%5C:Score=%5Cfrac%7BEarned%5C:Points%7D%7BMax%5C:Points%7D' alt='Decimal Score Formula'/>

| Assignment Name | Earned Points | Max Points | Decimal Score |
|---|:---:|:---:|:---:|
| Assignment 1 | 60 | 100 | 0.6 |
| Assignment 2 | 10 | 10 | 1.0 |
| **Total** |-|-|**1.6**

<img src='https://latex.codecogs.com/png.image?%5Cdpi%7B110%7D%5Cfg%7Bwhite%7D%5Cfrac%7B1.6%7D%7B2%7D=0.8%5Ctimes100=80%25' alt='Percent Average Example'/>

---

**In Summary**

In Point-Average categories, each assignment has its own weight, depending on the Max Points. A 100-point assignment is worth much more than a 10-point assignment.

In Percent-Average categories, each assignment is worth the same, regardless of the Max Points. A 100-point assignment has the same weight as a 10-point assignment.

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

## Troubleshooting

- Incorrect Calculations

    Most of the time, this is a result of one or both of two things:
    The Method is wrong, or there are other assignments that have been changed in this app, altering the results.
    
    First, make sure there are no edited assignments, by resetting that course.
    Compare the resulting grade with your grade on Schoology.
    (Make sure you're on the correct Grading Period!)

    If it still doesn't match, it's most likely an incorrect Calculation Method.
    Under each category title, there are buttons indicating "Calculation Type" which often default to "Point Average".
    Change these for your different categories, and compare each with Schoology to get the right configuration.

    It's possible that there are still issues with the calculation, such as certain assignments or categories not being counted.
    Carefully check your Schoology and compare it with the app to see if everything's there.
    Then, look at the [issues](https://github.com/macglencoe/Schoology-Streamlit/issues) on GitHub to see if anything there matches your issue.
    If not, please submit an issue detailing what is going wrong.
