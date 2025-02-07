<!---
    Copyright (c) 2018 Robert Bosch GmbH and its subsidiaries.
    This program and the accompanying materials are made available under
    the terms of the Bosch Internal Open Source License v4
    which accompanies this distribution, and is available at
    https://inside-docupedia.bosch.com/confluence/display/SCOS/BIOS+License+V4
-->

# Making contributions

* [Thank You!](#thank-you)
* [Quickstart, your first code contribution in 10 steps](#pr-recipe)
* [Community guidelines](#community-guidelines)
* [Whom to contact in case of questions](#whom-to-contact)
* [How to submit a bug report](#submitting-bug-reports)
* [How to submit a feature request](#submitting-feature-requests)
* [How to contribute code](#contributing-code)
    * [Coding conventions](#coding-conventions)
    * [Testing conventions](#testing-conventions)
    * [Branching conventions](#branching-conventions)
    * [Commit message conventions](#commit-message-conventions)
    * [Writing documentation](#writing-documentation)
    * [Pull Requests](#pull-requests)
        * [Conventions for communicating in Pull Request](#pr-signaling)
        * [Definition of done](#definition-of-done)
        * [General tips](#pr-tips)
* [Other contributions](#other-contributions)

**Note**: This is a template `CONTRIBUTING.md`. Please adapt to your specific
needs. For your convenience, we have placed a couple of placeholders throughout
the document - search for `$` to find them.

## <a name="thank-you">Thank You!</a>

Before we get to the _fine print_ and nitty gritty of contributing, let us 
start by saying **Thank you!** for considering to make a contribution to this
BIOS repository. BIOS exists and thrives because of people like you, who are 
willing to make contributions, share their knowledge with fellow developers
and subscribe to the ideas behind [Inner Source](http://paypal.github.io/InnerSourceCommons/)
in general. Kudos to you!

## <a name="pr-recipe">TL;DR: 10 Steps To Your First Pull Request.</a>

Ok, this is a long document so let's TL;DR this. The following recipe quickly
outlines ten steps to your first successful contribution in the form of a
pull request. 

1. First, create an issue in our 
[Issue Tracker](https://rb-wam.bosch.com/tracker/projects/BIOS) and describe the
contribution you intend to make.
2. We use [_git flow_](http://nvie.com/posts/a-successful-git-branching-model) 
as our branching model. So before you start coding, create a local feature 
branch, on which you will make your changes. We use the following template for 
naming feature branches:

        "feature/" <T&R Issue Key> "---" <Short description>
   
Here are some examples for valid feature branch names:

    feature/XYZ-1234---enhance-core2-documentation
    feature/XYZ-1234---bugfix-connection-intermittently-closes

You can also create a branch from within T&R, which will then automatically be
named according to our conventions (check out the _develop_ panel within T&R).
Note that you have to fetch the branch from our server, first, to start working
on it locally.
    
([More about our branching conventions](branching-conventions))
3. Make the changes in your local git repository and commit. ([More about our
   commit message conventions](#commit-message-conventions))
4. When you'd like to share your code and/or start a Pull Request to get
   feedback, push your commits to the repository.
5. Open the _Branches_ view in Bitbucket. Your newly pushed branch should show
   up there. Usually, all repositories have an associated build job which will
   pick up your new branch and build it. The result of the build will be
   presented in the _Builds_ column of the _Branches_ view. If the build fails
   and you know how to fix it, please do so before submitting a Pull Request.
   If you don't, go ahead and start a Pull Request anyway to allow us to help
   you make the build green.
5. In the _Branches_ view, click the ellipsis symbol in the _Actions_ column
   and select _Create Pull Request_.
6. In _Select source and destination_ dialog, make sure your new feature branch
   is selected as the _source_ branch and that the correct target branch is
   selected as well. In most cases, you will want to make _develop_ the target
   branch, as we are using the _git flow_ branching model. Click continue.
7. Enter a meaningful title, prefixed with the T&R issue number and possibly a
   slightly longer version of your branch name. Here is an example:

       XYZ-0815 - Add method to access nb. of received bytes to BusConnection
    
8. Briefly describe the changes you are submitting in the _Description_ field.
   The goal here is to make the life of the reviewers as easy as possible by
   explaining what you did and why. The description can be formatted as
   markdown, so feel free to format, add code examples, link to specific lines
   of code or even add sketches or diagrams. You can also @-mention anyone on
   Bitbucket to inform them of the PR (usually we do that by prefixing the
   @-mention with `/CC` or `/FYI`). ([More on our conventions
    for communicating within Pull Requests](#pr-signaling))
9. Every Pull Request will be reviewed and approved by at least one maintainer
   (see `readme.md`) before it is merged. We usually specify one or more
   default reviewer for each repository, so you don't necessarily have to
   specify a person here. If you'd like to request feedback from a specific
   person, though, feel free to add her as a reviewer here.
10. Click _Create Pull Request_ to start the review.

This is, in a nutshell, how you make contributions to this community. It may
sound complicated at first, but you'll quickly internalize the steps and will
be able to create a Pull Request in mere minutes or less. Please find a
detailed description in [How to contribute](#contributing-code).
    
## <a name="community-guidelines">Community guidelines</a>

$Community Name$ is a Bosch Internal Open Source (BIOS) community. We strive to 
work in accordance with the five BIOS/Social Coding values:

- _Openness_: We welcome *all Bosch associates* to make contributions,
  regardless of gender, age, sexual orientation, education, experience,
  affiliation with group, business unit, divition or other discriminating
  factors. 
- _Transparency_: We make our code, documentation and communication available
for everybody inside Bosch to see.
- _Voluntariness_: We prefer contributions to be made voluntarily by 
insinsically motivated community members.
- _Self-determination_: As a community, we ourselves decide *what* to work on, 
*when* to do it, with *which tools* we work and *what processes* we apply. 
- _Meritocracy_: Rank in our community is to be granted based on meritocratic
principles. That is: rank is determined by the amount and quality of 
contributions made to the community - both technically and socially. 

In our daily work, this means that

- we treat each other with utmost respect,
- we consider voluntary contributions as gifts and treat both our contributions
and our contributors accordingly,
- we happily invest time into sharing our knowledge with fellow community 
members, even if it slows down progress in the short term and
- we value communication "out in the open" (our forum, our issue tracker, 
in Pull Requests) to one-on-one communication.

## <a name="whom-to-contact">Whom to contact in case of questions?</a>

In order to allow as many people to benefit from the Q&A around 
our work, please consider to post any question you might have in 
our [discussion forum]($link to forum$).

If, for some reason, you prefer kicking off the collaboration in a personal
conversation, please contact the maintainers of this repository, which are
listed in this repository's `readme.md`.

## <a name="submitting-bug-reports">How to submit a bug report?</a> 

Found a bug? Great! A core task in improving our software is to identify any
flaws that may be present. The best place to report a bug is to [create an issue in
our issue tracker]($link to tracker$).

If you're not sure if what you are encountering is actually a 
bug or a feature, don't hesitate to contact us via our
[discussion forum]($link to forum$), first.

## <a name="submitting-feature-requests">How to submit a feature request?</a>

If you have suggestions for us on how to improve our code or
our documentation or have a new feature in mind, please by all 
means do let us know. The same rules apply as for bug reports:
either add a new issue outlining your suggestion in our 
[issue tracker]($link to tracker$) or [discuss it
first in our forum]($link to forum$).

## <a name="contributing-code">How to contribute?</a>

If you have fixed a bug or have developed that new feature 
you would like to make available to your fellow users, or even
if you have fixed whitespace or formatting issues, we'd like 
to encourage you to contribute that to our codebase. In this repository,
we use [_Pull Requests_](#pull-requests) to facilitate all contributions. Every
Pull Request will be peer reviewed by at least one community
member, which is a great way to get in touch with each other. 
You can [read about the details of making a contribution
here](https://inside-docupedia.bosch.com/confluence/display/SCOS/Contributing+Code+using+Bitbucket).

### <a name="coding-conventions">Coding Conventions</a> 

We have coding styleguides in place for all our projects. 

$describe your processes and tools to check/enforce code conventions$

#### Clean Code

More important than writing code that adheres to our styleguide is writing 
_Clean Code_. We consider code to be _clean_, if it

- works,
- is easy to understand,
- is easy to modify and 
- is easy to test.

Any code contribution will be reviewed by us with respect to these criteria.
We are more than happy and indeed consider it a core part of _being BIOS_ to
invest time mentoring junior developers to help them create _cleaner_ code and
to improve future contributions.

In addition to these principles of clean code, we also try to _design our
architectures for participation_. That, to us, means to avoid unnecessary
complexity, tight coupling or complex dependency relationships. 

### <a name="testing-conventions">Testing conventions</a>

We are convinced that writing testable code and writing tests is a precondition
for any software to be maintainable. Even though we do not prescribe fixed 
coverage thresholds for our tests, we encourage (and often will require) you to
write tests for code that needs to be maintainable where the effort is not 
excessive. This means, that we

- aim to write code with testability in mind (following the test first principle)
- write tests for everything we can test
- expose a submitted bug with a test first, before we implement a fix.

We also aim to write our tests such that they can be read as a specification
(because we usually don't spend time writing those). In practice, this means
that we use long, verbose and expressive names for tests which convey the 
condition being tested.

In our experience, writing tests can actually be a lot of fun. As a programmer,
you have more leeway to experiment and try new programming approaches when
writing tests. That is why we often try out new language features in our test 
code, first. And if you're following the test first principle, it's always 
quite rewarding to see those red test cases continue to turn green, once the
implementation is complete. Finally, only adequate tests will empower you to
continuously improve your codebase with refactorings, as they provide the 
reassurance that you didn't break anything accidentally. 

### <a name="branching-conventions">Branching conventions</a>

We implement the 
[_git flow_](http://nvie.com/posts/a-successful-git-branching-model). Write 
access to the `master`, `develop` and `release` branches is restricted to 
repository maintainers while everybody can create and push `feature` branches.
All changes on `develop` should be made by way of a merged and reviewed 
`feature` branch.

The following convention applies for naming feature branches:

    "feature/" <T&R Issue Key> "---" <Short description>
   
Here are some examples for valid feature branch names:

    feature/XYZ-1234---enhance-core2-documentation
    feature/XYZ-1234---bugfix-connection-intermittently-closes

Including the issue key in the branch name will automatically associate the
branch in Bitbucket with the issue and you'll be able to view issue details
from within Bitbucket and you an view branch details from within T&R.

### <a name="commit-message-conventions">Commit Message Conventions</a>

Commit messages on `feature` branches should briefly describe the change
introduced with the commit and should also contain the id of the issue or
issues which the change pertains to. Here are some examples of good 
commit messages:

    "Added method to access number of received bytes to BusConnection (XYZ-4711)"
    "XYZ-0815: Fixed typo in readme.md"

Following this convention automatically associates the commit, and thus the
branch and Pull Request that it belongs to with the given issue in T&R and
vice versa. 

### <a name="writing-documentation">Writing documentation</a>

We follow these principles when documenting code:

- We aim at keeping documentation as close the the asset being documented as
possible. That is, where sensible, we use inline code documentation. 
- We use [PlantUML](http://plantuml.com) for specifying UML diagrams in the 
code in order to be tool agnostic and allow everybody to adapt and improve it. 
- We favor [Markdown](https://daringfireball.net/projects/markdown) or other
text based means of generating documentation and try not to use proprietary
tools, such as Word or PowerPoint for that.
- We aim at providing our users with easy to understand instructions on how to 
use our code in each repositories `readme.md`.
- We favor code examples over analytical descriptions of our codebase.

### <a name="pull-requests">Pull Requests</a>

Pull Requests are our main vehicle for submitting, reviewing and merging new
code into our codebase. A Pull Request is more than just an easy interface to 
git: it is a powerful collaboration and communication tool. They are especially 
well suited to share knowledge and onboard new contributors. So if you are new 
to te community, submitting Pull Requests is an excellent way for you to engage
with us and for us to help you get started. Discussions and the Q&A that often
accompanies Pull Requests are archived and linkable and we thus use them to
disseminate knowledge about our codebase. 

#### <a name="pr-signaling">Conventions for communicating in Pull Requests</a>

[This article](https://bit.ly/2DLqmBx) 
nicely summarizes how to (and how not to) communicate in Pull Requests. Apart
from the social aspects of interactions, we follow a couple of conventions for
signaling - that is: using the various technical means of communicating in
Pull Requests that are afforded to us by Bitbucket (our Social Coding platform).

Here are common signals and how you use our platform to set them.

- **Add s.o. as reviewer**: _"I'd like you to review my PR and I will not merge w/o your approval!"_
- **Approve a PR**: _"I'm ok with merging this PR. If there are open tasks, I expect these to be finished before merging and I trust you to do this w/o another review!"_
- **PR Needs Work**: _"I am not ok with merging this PR and I require changes to be made. I will re-review this PR after changes are made!"_
- **@-mention s.o. in PR description with /CC prefix**: _"I'd like you to have a look at this PR but I'm not asking for your formal approval!"_
- **@-mention s.o. in PR description with /FYI prefix**: _"Just so you know, we're working on this!"_
- **@-mention s.o. in comment as part of question**: _"Can you please reply to my question with a comment?"_
- **Reviewer adds task to PR**: _"This needs to be fixed before I merge this PR!"_
- **Author of PR adds task in response to comment of reviewer**: _"I will finish this** task before merging!"_
- **Mark task as completed**: _"This task is finished and I have pushed the changes!"_
- **Add like**: _"I agree with the statemens made in the liked comment!"_
- **Add link to T&R issue**: _"I wil not make the change in this PR but will take care of it later!"_

Generally speaking, when signalling, try to

- be respectful,
- be concise, 
- be specific,
- clearly state your expectation and
- use links where possible (to files, lines in files, commits, pull requests, people, issues, other comments, ...)

#### <a name="definition-of-done">Definition of done</a>

We use the following checklist to determine if a PR is ready to merge:

- The last build is _green_
- If new code was added or if a bug was fixed, corresponding tests have been added
- All tasks added by reviewers are resolved
- At least one maintainer has approved the PR and none has signaled _Needs Work_

#### <a name="pr-tips">General tips</a>

- Keep your PRs as small as possible. The smaller the PR the higher the 
velocity of review and acceptance.
- Avoid conflating multiple issues in one PR. Aside from that usually leading 
to huge PRs and it making the job of a reviewer unnecessarily harder, it will also confuse the automated T&R issue state transition feature we use. 
- Write a good description to allow the reviewer to quickly get an overview of
your changes.
- Don't add more than two reviewers if you expect all of them to review. This will most likely block you.

## <a name="other-contributions">Other contributions</a>

You don't have to be a coder to make a valuable contribution to this community!
There are many contributions that you can make as a non-coder that will be very
valuable to the community, such as

- giving feedback of any kind,
- reporting bugs,
- requesting features,
- adding new or improvements existing documentation,
- helping other users to use our software,
- asking and/or answering questions in our forums,
- promoting BIOS, Social Coding, our community and our software within Bosch or
- designing artwork for both our software, our wiki or our Bosch connect presence.

May the source be with you!

<!---
    Copyright (c) 2018 Robert Bosch GmbH and its subsidiaries.
    This program and the accompanying materials are made available under
    the terms of the Bosch Internal Open Source License v4
    which accompanies this distribution, and is available at
    https://inside-docupedia.bosch.com/confluence/display/SCOS/BIOS+License+V4
-->
