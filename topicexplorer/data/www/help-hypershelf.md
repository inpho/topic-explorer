This is the **“Hypershelf”**.  It allows you to explore documents in the corpus using pre-trained topic models.  If you are unfamiliar with topic modeling, you can watch the video at [Inphodata.cogs.indiana.edu](http://inphodata.cogs.indiana.edu) and read an article by [David Blei (2012)](http://www.cs.columbia.edu/~blei/papers/Blei2012.pdf). 

## Document Similarity

The **Hypershelf** shows up to 40 **documents** that are **most similar to** the **focal document**.  Each document is represented by a bar whose colors show the **mixture and proportions of topics** assigned to each document by the training process. The **relative lengths** of the bars **indicate** the **degree of similarity** to the focal document according to the topic mixtures.

## Topics 

**Rolling over** a colored segment shows the **highest probability words** associated with the topic. The **key** on the right shows all the topics identified by the model. If you **click on a topic** in the bar or the key, the display will **sort** the **current documents ranked according to that topic**. In this topic-sorted mode, a **Top Documents** button appears at the top that lets you retrieve the documents from the entire corpus that are most similar to that topic.

## Focal Document 

To select a new **focal document** you can:
1. **Start typing a few letters** in the focal document entry area;
2. **Click the crossed arrows button** to the right of the focal document entry area for a **random** document;
3. **Refocus** on one of the already-displayed documents by moving the cursor just to the **left of the topic bar** and **clicking** on the **arrow** that appears.

You may use the button to the right of the random document button to visualize the focal document and you may use the dropdown menu attached to the button to **switch** to a model with a different **number of topics**.

## Other Options

Below the key are some additional display options that let you **sort** the displayed documents **alphabetically**, or to **normalize** the **bar lengths** so that you can compare the document mixtures more directly.

Other icons to the left of each topic bar allow you to **view the document contents**, or see a **"fingerprint"** of the topic mixtures for that document in all the available models with different numbers of topics.  Clicking on a bar in the fingerprint will take you to a hypershelf focused on the selected document with that given model.

The numbers in the menu on the left can be used to **navigate directly to a model** with that number of topics.

Above the numbers on the left, the topic cluster button will take you to a different interface that lets you **explore topic similarity across the models**. 

The home button at the top left will take you to a **general information page** about the corpus and models.
