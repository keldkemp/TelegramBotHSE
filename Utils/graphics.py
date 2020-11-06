import matplotlib.pyplot as plt
from DB.DataBasePG import DataBasePg


def lineplot(x_data, y_data, x_label="", y_label="", title=""):
    # Create the plot object
    _, ax = plt.subplots()

    # Plot the best fit line, set the linewidth (lw), color and
    # transparency (alpha) of the line
    ax.plot(x_data, y_data, lw=2, color='#539caf', alpha=1)

    # Label the axes and provide a title
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)


db = DataBasePg()
list = db.get_stat()
list_date = []
list_req = []
for ls in list:
    list_date.append(ls[1])
    list_req.append(ls[0])

lineplot(list_date, list_req)
plt.show()
