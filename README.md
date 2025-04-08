<a href="https://www.buymeacoffee.com/randompers0" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
# Internal-Form-Generator
Hello,

This python code generates any form you want, and allows you to add media in it such as video, images, or sound. To get this code in an executable format, you have to download the file called "Internal_Form_Generator_Version_A", to get the raw python code, download "Internal_Form_Generator_Raw_Code" folder. Before you you actually run the code, it is best to edit the default questions in the form to the one that you need. To do this, open the "Change_Form" folder. This is the same folder in both the executable versions:

![alt text](https://github.com/DonNguyen123/Internal-Form-Generator/blob/42966a9c281d14423f3b33aea6db18f5169d9a2e/Example%20Images/File_Organization_Executable.png)

And the raw code version:

![alt text](https://github.com/DonNguyen123/Internal-Form-Generator/blob/42966a9c281d14423f3b33aea6db18f5169d9a2e/Example%20Images/File_Organization_Raw_Code.png)

There, you will find several text and csv files:

![alt text](https://github.com/DonNguyen123/Internal-Form-Generator/blob/42966a9c281d14423f3b33aea6db18f5169d9a2e/Example%20Images/Main_Form_Editing.png)

In this case, you will start with opening the "Questions.txt", and editing it. It can be said that the questions and media must be in a specific format, the details of which are below: 

# Form Configuration Guidelines

1. Every question and piece of media named should have a lineskip inbetween each other.

2. You may only add a modifier (shown in the image below in red) to the end of the question/media statement. There should be no space between the modifier and the end of the question/media statement. The modifiers that can be used are:
   - **A. `<long>`**: Makes the text box bigger in height to allow you to see more text as you type. Note that you may type as much text as you want regardless of the size of the textbox.
   - **B. `<integer>`**: Makes sure that, when the form is submitted, the value in the textbox is an integer. Otherwise, an error warning will appear. Remember that an integer in this case is any number without a decimal place, such as: 5, -7, -12. Note that the format will not allow commas, so use 1293, and not 1,293.
   - **C. `<number>`**: Makes sure that, when the form is submitted, the value in the textbox is a number. Otherwise, an error warning will appear. Note that like the integer, it also takes negatives, and does indeed take decimal places, such as: -12.34, 34.56, 1234.5.
   - **D. `<text>`**: Makes sure that, when the form is submitted, the value in the textbox is text. Otherwise, an error warning will appear.

3. If there is no modifier, it is assumed that the textbox will take both alphabetical and numerical values.

4. The order of the questions and the media is dependent on the order in the Question.txt document. So if A.png is before Question A in the text document, then it will show up that way in the form.

5. If a media is called, then it must be done with its file name and extension (e.g., `The_Merchant_of_Hell.png`). The actual video/image/sound that is called in the question document must be in the "Media_Data" folder, which is in the same directory as the "Change_Form" folder. Note that the name of the file called and the name of the media in the "Media_Folder" must be the same.An example of correct formatting can be shown in the image below:

![alt text](https://github.com/DonNguyen123/Internal-Form-Generator/blob/42966a9c281d14423f3b33aea6db18f5169d9a2e/Example%20Images/Question_Format.png)

After this is done, save the "Questions.txt". Then, if it is needed, change the disciption of the form, in the "Discription.txt", and the saving location of the responses in the form in "Remote_Link.txt". Note that both files are in the same directory as "Questions.txt". It can be said that the "Discription.txt" has no format requirment. However, "Remote_Link.txt" should have the link without any quotations. Note that outside of local links or a direct access shared directory, you will probably need to edit the raw python version to include athentication access or api to where ever you need to send the data. When you are done editing, everything, you may now run the code. An example of what the form that is produce could look look like can be seen below:

![alt text](https://github.com/DonNguyen123/Internal-Form-Generator/blob/42966a9c281d14423f3b33aea6db18f5169d9a2e/Example%20Images/Example_Form_A.png)

![alt text](https://github.com/DonNguyen123/Internal-Form-Generator/blob/42966a9c281d14423f3b33aea6db18f5169d9a2e/Example%20Images/Example_Form_B.png))

Note that from these images, you can fine some useful features. You may scroll up and down the form with the right scrollbar if nessiarly. If you need to scroll in the textbox, please just click the textbox, and use the up and down arrows in your keyboard. Note that the images will display directly in the form, while the sound and video (which can be activated by double clicking the blue links are underlined in red in the images above) will use a vlc player. This player is automaticlly attached to the code, meaning you do not need to downlaod anything. It will just work. Note, that when you submit the form, it will go by default in the "Change_Form" directory as "Responses.csv". Alterntively, if you actually did bother to change "Remote_Link.txt", it will save where the at the location you put in there.

It should be stated for full clarity that the main purpose of this code is used for small applications, that generally offline. For example, you could use this as an internal form on a tablet that customers that enter or leave your store, can rate how well the services are. Or when people in get a line for a charity event, and you wish to to record who they are. Even a classroom exit would be doable in this case, or a small personal note app that you record your activites in. In general, however, if you need people to access a form online from far away, it is better to just use google forms. If you want bigger applications, please just use an SQL based database.

