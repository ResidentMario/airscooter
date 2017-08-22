Quickstart
==========

Motivation
----------

Data distributed via the web can do so in any of a number of different "packaging format". We may find that the
traffic estimates that we need for one project are wrapped up inside of a formatted Excel file, or that the
archived feed data that we need for another project is delivered in the form of a packet of files inside of a
compressed ZIP files.

These shreds of data are hopefully relatively easy for you, the project author, to clean up and refactor into the
form you need them to be in. But for anyone else reading your code, this imposes the mental overhead of
understanding *what* it is, exactly, that they need to do to get that data properly marshaled themselves.

But what if you work with colleagues or collaborators or copycats who want to get your project running themselves? Or,
better yet, what if you come back to this project again a few months from now. Will you remember what piece of data
engineering goes where? I doubt it.

``airscooter`` foolproofs simple data processing pipelines. It does this by boling data fetches down to a single
terminal command.

Use Case
--------

To learn more, let's step through a use case (`you can clone this example yourself`_).

.. _you can clone this example yourself: https://github.com/ResidentMario/airscooter-quickstart-example

Suppose that you're an analyst at a traffic planning consulting firm. You've been hired by the city of New York to
help plan rolling out additional bike lines around the lower Manhattan region. As consultants are wont to do, you are
writing a report that you hope will present a thoughtful data-driven summary on New York City biking past and,
hopefully, future.

One dataset that piques your interest is the `NYC DOT East River Bicycle Counts dataset`_. However, when you download
this data you see that not only is the data split across several files, organized by month, but that furthermore
it's locked inside of formatted Excel files:

.. image:: http://i.imgur.com/dsamllb.png

.. _NYC DOT East River Bicycle Counts dataset: https://data.cityofnewyork.us/Transportation/Bicycle-Counts-for-East-River-Bridges/gua4-p9wg

Let's write a couple of one-off scripts for processing this data. The first of these is ``depositor.py``. All this
does is download the data and store it locally: ::

    import requests
    r = requests.get("https://data.cityofnewyork.us/download/gua4-p9wg/application%2Fzip")
    with open("nyc-east-river-bicycle-counts.zip", "wb") as f:
        f.write(r.content)

This script is basically a network test: it makes sure that the data is still where we think it should be. Next we'll
write a ``transform.py``, which actually chews through this data and transform it into something you can actually
use. This will go something like this: ::

    from zipfile import ZipFile
    from calendar import monthrange
    import os
    import pandas as pd

    z = ZipFile("nyc-east-river-bicycle-counts.zip", "r")
    z.extractall()

    xlsx_list = sorted([file for file in os.listdir(".") if "xls" in file.rsplit(".")[-1]])

    data_by_month = []

    for i, xlsx in enumerate(xlsx_list):
        days_in_month = monthrange(2016, i + 4)[1]
        data = (pd.read_excel("04 April 2016 Cyclist Numbers for Web.xlsx", skiprows=4, header=1)
                .iloc[:days_in_month, 1:-1])
        data_by_month.append(data)

    unified_data = pd.concat(data_by_month)
    unified_data = unified_data[unified_data['Date'] != 'T = trace of precipitation']
    unified_data.reset_index(drop=True, inplace=True)
    unified_data.to_csv("nyc-east-river-bicycle-counts.csv")

    for fp in [file for file in os.listdir(".") if "xls" in file.rsplit(".")[-1]]:
        os.remove(fp)
    os.remove("Bicycle Counts for East River Bridges Metadata.docx")
    os.remove("nyc-east-river-bicycle-counts.zip")

To fully process this data, therefore, we need to do two things: download it, then parse it. That means we have to
tell our users to run ``python depositor.py`` then ``python transform.py`` from the terminal, in that order.

Simple enough. But we can make things even simpler with ``airscooter``.

Begin by running the following in the terminal: ::

    airscooter init

This will initialize a ``.airflow`` folder inside of the current directory, and configure everything inside of it as
an ``airscooter`` package. Then, back at the command line, run: ::

    airscooter link depositor.py --outputs=["nyc-east-river-bicycle-counts.zip"]
    airscooter link transform.py --inputs=["nyc-east-river-bicycle-counts.zip"] --outputs=["nyc-east-river-bicycle-counts.csv"]

Behind the scenes, ``airflow`` figures out that to run ``transform.py``, we logically need ``depositor.py`` to
succeed. So it configures itself to run them in dependency order: first, run the task that generates the data; then,
run the task that processes it. Downloading is the job of our **depositor task**; translating the resulting files
into something useful is the job of our **transform task**. Together, these two operations make up a rudimentary
**task graph**.

Building such simple, executable task graphs is what ``airscooter`` is all about. From now on, if we want to
regenerate this same data again, we can do so with just one terminal command: ::

    airscooter run

This, in a nutshell, is all ``airscooter`` does. Write a bunch of process files that do stuff (currently, ``py``,
``ipynb``, and ``sh`` files are supposed), then run a few ``airscooter link`` commands through the command line to
thread them all together. The next person need only execute ``airscooter run`` to put Humpty Dumpty back together again.

Why
---

Our overly simple example doesn't explain *why* we want to do this. If ``nyc-east-river-bicycle-counts.csv``
is a one-off thing, you can get away with just documenting how you got the data in a ``README.md`` in a GitHub
repository. However, the additional formality that ``airscooter`` introduces is extremely useful when you start to do
this at scale.

Imagine that we have simple data engineering tasks like this one: but *lots* of them. The project for which
``airflow`` was originally developed theoretically needed to manage running hundreds of these simple tasks. This is
an altogether common scenario, as any data analytics shop that isn't in the business of creating data likely has many
poorly documented "fetch scripts" lying about. If your team can converge on saving their work in this format, you can
save yourself a lot of what-was-this-person-thinking headaches down the road. And if you want to start running such
tasks *systematically* (as I did), standardized one-button runnability is an absolute necessity.

Or, imagine that we have one such data engineering task, but it's *huge*. Many different moving parts are involved;
you're fetching data from three, five, ten different raw files to compose your resultant dataset. There are so many
steps involved that our little ``README.md`` note is now ineffectual. ``airscooter`` is extremely helpful in this
scenario because it lets you standardize your runtime methodology. To puzzle back together the order things are meant
to be run in, just inspect the ``airscooter`` task graph. To run them all, just run ``airscooter run``. The
underlying if-this-then-that may be complicated, but the end result will still be transparent to collaborators,
copycats, and six-months-older self that have to regenerate the data for themselves without present-you input.