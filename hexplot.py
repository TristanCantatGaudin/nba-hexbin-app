import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc

def seasons_of_player( playerId ):
    df = pd.read_html('https://www.basketball-reference.com/players/%s.html' % (playerId) )
    try:
        seasons = df[0]['Season']
        games_played = pd.to_numeric(df[0]['G'], errors='coerce') 
    except:
        seasons = df[1]['Season']
        games_played = pd.to_numeric(df[1]['G'], errors='coerce')         
    seasons_played = seasons[ games_played>0 ]
    seasons_with_shots = [s for s in seasons_played if '-' in s and (int(s.split('-')[0])>=1996)]
    return seasons_with_shots

st.set_page_config(page_title='NBA shots', page_icon=":basketball:")

st.sidebar.title('Mapping NBA shots')

playerId = {
'Rat Allen':'a/allenra02',
'Kobe Bryant':'b/bryanko01',
'Stephen Curry':'c/curryst01',
'James Harden':'h/hardeja01',
'Allen Iverson':'i/iversal01',
'Michael Jordan':'j/jordami01',
'Damian Lillard':'l/lillada01',
'Karl Malone':'m/malonka01',
'Reggie Miller':'m/millere01',
'Dirk Nowitzki':'n/nowitdi01',
"Shaquille O'Neal":'o/onealsh01',
'Trae Young':'y/youngtr01',
'Victor Wembanyama':'w/wembavi01',
}


selected = st.sidebar.selectbox('Select a player:', ['']+list(playerId.keys()), format_func=lambda x: '...' if x == '' else x)



if selected:
    #st.success('Yay! 🎉')
    seasons_with_shots = seasons_of_player( playerId[selected] )
    season = st.sidebar.selectbox('Season:',seasons_with_shots)
    if season:
        seasonYearEnd = str(int(season.split('-')[0]) + 1)
        urlShots = 'https://www.basketball-reference.com/players/%s/shooting/%s' % (playerId[selected],seasonYearEnd)
else:
    st.warning('No player selected')
    urlShots = ''
    
    
# Checkboxes:
left, right = st.sidebar.columns(2)
with left: 
    draw_court_box = st.sidebar.checkbox('Draw court',value=True)
with right:
    draw_title_box = st.sidebar.checkbox('Add title',value=True)


def draw_court(ax=None, color='black', lw=2, outer_lines=False):
    # If an axes object isn't provided to plot onto, just get current one
    if ax is None:
        ax = plt.gca()

    # Create the various parts of an NBA basketball court

    # Create the basketball hoop
    # Diameter of a hoop is 18" so it has a radius of 9", which is a value
    # 7.5 in our coordinate system
    hoop = Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False)

    # Create backboard
    backboard = Rectangle((-30, -7.5), 60, -1, linewidth=lw, color=color)

    # The paint
    # Create the outer box 0f the paint, width=16ft, height=19ft
    outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color,
                          fill=False)
    # Create the inner box of the paint, widt=12ft, height=19ft
    inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color,
                          fill=False)

    # Create free throw top arc
    top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180,
                         linewidth=lw, color=color, fill=False)
    # Create free throw bottom arc
    bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0,
                            linewidth=lw, color=color, linestyle='dashed')
    # Restricted Zone, it is an arc with 4ft radius from center of the hoop
    restricted = Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw,
                     color=color)

    # Three point line
    # Create the side 3pt lines, they are 14ft long before they begin to arc
    corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw,
                               color=color)
    corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
    # 3pt arc - center of arc will be the hoop, arc is 23'9" away from hoop
    # I just played around with the theta values until they lined up with the 
    # threes
    three_arc = Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw,
                    color=color)

    # Center Court
    center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0,
                           linewidth=lw, color=color)
    center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2=0,
                           linewidth=lw, color=color)

    # List of the court elements to be plotted onto the axes
    court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw,
                      bottom_free_throw, restricted, corner_three_a,
                      corner_three_b, three_arc, center_outer_arc,
                      center_inner_arc]

    if outer_lines:
        # Draw the half court line, baseline and side out bound lines
        outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw,
                                color=color, fill=False)
        court_elements.append(outer_lines)

    # Add the court elements onto the axes
    for element in court_elements:
        ax.add_patch(element)

    return ax


def html_to_shot_table( html ):
	full_table = []
	for line in str(html).split('<div class="shot-area">')[1].split('<div'):
	    if 'style="top:' in line:
	        top = int(line.split('top:')[1].split('px')[0])
	        left = int(line.split('left:')[1].split('px')[0])
	        game = line.split('tip="')[1].split('<br>')[0]
	        clock = line.split('<br>')[1].split('<br>')[0]
	        description = line.split('<br>')[2]
	        score = line.split('<br>')[3].split('"')[0]
	        made = 1
	        if 'tooltip miss' in line:
	            made = 0
	        #print(line)
	        #print(top,left,game,clock,description,score)
	        full_table.append( [top,left,game,clock,description,score,made] )
	return full_table



# get the html:
from urllib.request import urlopen
if 'http' in urlShots:
	st.write('Data from:',urlShots)

	html = urlopen(urlShots).read()
	full_table = html_to_shot_table( html )
	
	import pandas as pd
	df = pd.DataFrame(full_table,
	                  columns='top,left,game,clock,description,score,made'.split(','))
	X = -1*df['left'] + 240
	Y = df['top'] - 45
	
	hbMade = plt.hexbin(X[ df['made']==1 ], Y[ df['made']==1 ], gridsize=(40,20), cmap='cool',
	               extent=(-250,250,-50,420) )
	hbMissed = plt.hexbin(X[ df['made']==0 ], Y[ df['made']==0 ], gridsize=(40,20), cmap='cool',
	               extent=(-250,250,-50,420) )
	
	plt.clf() # to flush the two plots we just made: we only wanted to catch the output
	pctMade = hbMade.get_array() / (hbMade.get_array() + hbMissed.get_array())
	
	# Now convert these numbers to colours:
	import numpy as np
	pctMade[ np.isnan(pctMade) ] = 0
	
	plt.figure(figsize=(9,8.5))
	plt.subplot(111,facecolor='k')
	draw_court(outer_lines=True, color="#777777")
	plt.xlim(-251,251)
	plt.ylim(-47,423)
	plt.gca().set_facecolor('k')
	hb = plt.hexbin(X, Y, gridsize=(40,20), cmap='turbo',
	               extent=(-250,250,-50,420))
	total_count = hb.get_array()
	# convert the number to size:
	new_size = 0.005*total_count
	new_size[ new_size>0.1 ] = 0.1
	plt.clf()
	
	
	
	# Replot:
	plt.figure(figsize=(9,8.5),facecolor='#111111')
	plt.subplot(111,facecolor='#111111')
	if draw_court_box:
	    draw_court(outer_lines=True, color="#777777")
	plt.xlim(-252,252)
	plt.ylim(-50,425)
	plt.xticks([]); plt.yticks([])
	plt.gca().set_facecolor('k')
	hb = plt.hexbin(X, Y, gridsize=(40,20), cmap='cool',
	               extent=(-250,250,-50,420),
	               sizes=new_size)
	
	ax = plt.gca()
	ax.figure.canvas.draw()
	# Now iterate over bins to change their colours:
	fcolors = hb.get_facecolors()
	for iii in range(len(fcolors)):
	    if pctMade[iii] < 0.1:
	        fcolors[iii] = [1., 0., 0., 1.]
	    elif pctMade[iii] > 0.5:
	        fcolors[iii] = [0.6, 1., 0.2, 1.]
	    else:
	        fcolors[iii] = [0.9, 0.9, 0.9, 1.]        
	hb.set(array=None, facecolors=fcolors)
	
	if draw_title_box:
		plt.text(-230,390,selected,color='w',fontsize=20,fontweight='bold')
		plt.text(-230,360,season,color='w',fontsize=18,fontweight='bold')
	
	
	st.pyplot(plt.gcf())
