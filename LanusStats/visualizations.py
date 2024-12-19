import matplotlib.pyplot as plt
import pandas as pd
import urllib
import numpy as np
from mplsoccer import PyPizza, add_image, FontManager, VerticalPitch, Pitch
from PIL import Image
from urllib.request import urlopen
from matplotlib.patches import RegularPolygon
import matplotlib.patheffects as path_effects
from matplotlib.offsetbox import (OffsetImage,AnnotationBbox)
from .exceptions import MatchDoesntHaveInfo
from .fbref import Fbref
from .fotmob import FotMob
from .functions import semicircle
from .config import soc_cm
from .threesixfivescores import ThreeSixFiveScores
from .transfermarkt import Transfermarkt
fbref, fotmob, threesixfivescores, transfermarkt = Fbref(), FotMob(), ThreeSixFiveScores(), Transfermarkt()

#Fonts
font_normal = FontManager('https://raw.githubusercontent.com/googlefonts/roboto/main/'
                            'src/hinted/Roboto-Regular.ttf')
font_italic = FontManager('https://raw.githubusercontent.com/googlefonts/roboto/main/'
                                'src/hinted/Roboto-Italic.ttf')
font_bold = FontManager('https://raw.githubusercontent.com/google/fonts/main/apache/robotoslab/'
                                'RobotoSlab[wght].ttf')
title = FontManager('https://github.com/google/fonts/blob/main/ofl/bungeeinline/BungeeInline-Regular.ttf?raw=true')

def fbref_plot_player_percentiles(path, image=None, chart_stats=None, save_image=False, name_extra='', credit_extra=''):
    """Does a pizza plot with percentiles (eg: https://mplsoccer.readthedocs.io/en/latest/gallery/pizza_plots/plot_pizza_dark_theme.html#sphx-glr-gallery-pizza-plots-plot-pizza-dark-theme-py)
    for a specific player, if they have their percentiles in their fbref page.

    Args:
        path (str): URL to a player page in Fbref. Example: https://fbref.com/en/players/90a0bb3b/Victor-Malcorra
        image (str, optional): Path to an image so it can be at the center of the plot. Defaults to None. Recommended to use this: https://crop-circle.imageonline.co/
        chart_stats (list, optional): Adds rectangles above the image to indicate sections of the plot. Defaults to None. Use a list.
        save_image (bool, optional): Saves a png of the plot. Defaults to False.
        name_extra (str, optional): Something to add to the title. Defaults to ''.
        credit_extra (str, optional): Something to add to the credits. Defaults to ''.
    """
    
    #Define player dataframe and also colors of the plot
    print('Gettings player percentiles...')
    player_df = fbref.get_player_percentiles(path=path)
    
    slice_colors, text_colors = fbref.get_slice_text_colors(player_df)

    #Define strings of parameters and shortens some that are long. You can add more.
    params = list(player_df.iloc[:, 0].dropna())
    params_short = {
        'npxG: Goles esperados (xG) sin contar penaltis': 'npxG',
        'npxG: Non-Penalty xG': 'npxG'
    }
    for index, value in enumerate(params):
        if value in params_short:
            params[index] = params_short[value]
    plot_params = []
    for param in params:
        if len(param.split(' ')) > 2:
            initial_list, final_list = param.split(' ')[:2], param.split(' ')[2:]
            final_string = ' '.join(initial_list) + '\n' + ' '.join(final_list)
            new_param = final_string
        else:
            new_param = param
        plot_params.append(new_param)

    #Define values for the plot
    values = list(player_df.iloc[:, 2].dropna().astype(int))

    #Define PyPizza class and plot it
    print('Starting to plot...')
    baker = PyPizza(
        params=plot_params,                  
        background_color="#222222",     
        straight_line_color="#000000",  
        straight_line_lw=1,             
        last_circle_color="#000000",    
        last_circle_lw=1,               
        other_circle_lw=0,              
        inner_circle_size=20            
    )

    fig, ax = baker.make_pizza(
        values,                          
        figsize=(8, 8.5),                
        color_blank_space="same",        
        slice_colors=slice_colors,        
        value_colors=text_colors,         
        value_bck_colors=slice_colors,    
        blank_alpha=0.4,
        kwargs_slices=dict(
            edgecolor="#000000", zorder=2, linewidth=1
        ),                               
        kwargs_params=dict(
            color="#F2F2F2", fontsize=10,
            fontproperties=font_bold.prop, va="center"
        ),                               
        kwargs_values=dict(
            color="#F2F2F2", fontsize=11,
            fontproperties=font_normal.prop, zorder=3,
            bbox=dict(
                edgecolor="#000000", facecolor="cornflowerblue",
                boxstyle="round,pad=0.2", lw=1
            )
        )                               
    )

    #Define all the text in the plot
    name = path.split('/')[-1].replace('-', ' ')
    
    #Credits. Don't delete them. I will find you.
    if path.split('/')[3] == 'es':
        CREDIT_1 = f"Data: Fbref | Código: LanusStats | Inspirado por: MPLSoccer {credit_extra}"
        CREDIT_2 = "A mayor valor de la barra, signfica que está entre los números más altos de la categoría"
        CREDIT_3 = "Jugador comparado con otros de su misma posición en ligas de nivel similar el último año."
    else:
        CREDIT_1 = f"Data: Fbref | Code: LanusStats | Inspired by: MPLSoccer {credit_extra}"
        CREDIT_2 = "If the value of the bar is larger, it's in the highest values of the category"
        CREDIT_3 = "Player compared to positional peers in leagues of the same caliber over the last 365 days."

    fig.text(0.99, 0.02, f"{CREDIT_1}\n{CREDIT_2}\n{CREDIT_3}", size=10, fontproperties=font_italic.prop, color="#F2F2F2",ha="right")

    if chart_stats:
        #Add text near the rectangles
        fig.text(0.34, 0.925, f"{chart_stats[0]}", size=16, fontproperties=font_bold.prop, color="#F2F2F2")
        fig.text(0.492, 0.925, f"{chart_stats[1]}", size=16, fontproperties=font_bold.prop, color="#F2F2F2")
        fig.text(0.662, 0.925, f"{chart_stats[2]}", size=16, fontproperties=font_bold.prop, color="#F2F2F2")

        # add rectangles
        fig.patches.extend([
            plt.Rectangle(
                (0.31, 0.9225), 0.025, 0.021, fill=True, color="#1a78cf",
                transform=fig.transFigure, figure=fig
            ),
            plt.Rectangle(
                (0.462, 0.9225), 0.025, 0.021, fill=True, color="#ff9300",
                transform=fig.transFigure, figure=fig
            ),
            plt.Rectangle(
                (0.632, 0.9225), 0.025, 0.021, fill=True, color="#d70232",
                transform=fig.transFigure, figure=fig
            ),
        ])
        fig.text(
            0.515, 0.975, f"{name}{name_extra}", size=30,
            ha="center", fontproperties=title.prop, color="#F2F2F2"
            )
    else:
        fig.text(
            0.515, 0.94, f"{name}{name_extra}", size=30,
            ha="center", fontproperties=title.prop, color="#F2F2F2"
            )

    #Define image
    if image:
        #Page to generate round images: https://crop-circle.imageonline.co/
        ax_image = add_image(
            Image.open(image), fig, left=0.4478, bottom=0.4315, width=0.13, height=0.127
        )

    if save_image:
        print('Saving image...')
        plt.savefig(f'{name} fbref percentile plot.png', dpi=300, bbox_inches='tight')
        
def fotmob_match_momentum_plot(match_id, save_fig=False):
    """Plot Match Momentum
    Args:
        match_momentum_df (DataFrame): DataFrame generated in match_momentum functions. Contains two columns: Minute and value (if > 0, momentum was with home side and viceversa)
        match_id (string): Match Id for a FotMob match. Example: https://www.fotmob.com/es/matches/man-city-vs-crystal-palace/2ri9zd#4193843
        save_fig (bool, optional): Save figure or not.
    Returns:
        fig, ax: A png and the fig and axes for further customization
    """
    response = fotmob.request_match_details(match_id)
    home_color, away_color = fotmob.get_team_colors(match_id)
        
    try:
        match_momentum_df = pd.DataFrame(response.json()['content']['matchFacts']['momentum']['main']['data'])
    except KeyError:
        raise MatchDoesntHaveInfo(match_id)
    
    plot_colors = [f'{home_color}' if value < 0 else f'{away_color}' for value in match_momentum_df.value]

    fig,ax = plt.subplots(figsize=(16,9))
    fig.set_facecolor('white')
    

    ax.bar(match_momentum_df.minute, match_momentum_df.value, color=plot_colors)
    ax.axvline(45.5, ls=':')
    ax.set_xlabel('Minutes')
    ax.set_xticks(range(0,91,10))
    ax.set_xlim(0,91)

    plt.gca()
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.set_yticks([])
    if save_fig:
        plt.savefig(f'{match_id}_match_momentum.png', bbox_inches='tight')

    return fig, ax

def fotmob_hexbin_shotmap(league, season, player_id, credit_extra=' ', save_fig=False):
    """Gets a player, league and season and plots an hexbin plot of the shots that player took in that tournament according to FotMob page.
    Inspired and most of the code is by: https://github.com/sonofacorner/soc-viz-of-the-week

    Args:
        league (str): Possible leagues in get_available_leagues("Fotmob")
        season (str): Possible saeson in get_available_season_for_leagues("Fotmob", league)
        player_id (str): FotMob Id of a player. Could be found in the URL of a specific player.
                            Example: https://www.fotmob.com/es/players/727095/ignacio-ramirez
                            727095 is the player_id.
        credit_extra (str, optional): If you want to add your name or handle. Defaults to ' '.
        save_fig (bool, optional): Saves the image to a png. Defaults to False.
    """
    df = fotmob.get_player_shotmap(league, season, player_id)
    
    df = df[df['situation'] != 'Penalty']
    
    first_row = df.iloc[0]
    team_id = first_row.get('teamId')
    team_name = np.where(team_id == first_row['homeTeamId'], first_row['homeTeamName'], first_row['awayTeamName']).item()

    data = df[['eventType', 'playerName', 'x', 'y', 'expectedGoals', 'teamId', 'teamColor', 'teamColorDark']]
    plt.rcParams['hatch.linewidth'] = .02
    fig, ax = plt.subplots(figsize=(8,6), dpi=300)
    pitch = VerticalPitch(
        pitch_type='custom',
        half=True,
        goal_type='box',
        linewidth=1.25,
        line_color='black',
        pad_bottom=-8,
        pad_top=13,
        pitch_length=105,
        pitch_width=68
    )
    pitch.draw(ax = ax)

    bins = pitch.hexbin(x=data['x'], y=data['y'], ax=ax, cmap=soc_cm, gridsize=(14,14), zorder=-1, edgecolors='#efe9e6', alpha=0.9, lw=.25)

    x_circle, y_circle = semicircle(104.8 - data['x'].median(), 34, 104.8)  # function call
    ax.plot(x_circle, y_circle, ls='--', color='red', lw=.75)

    annot_x = [54 - x*14 for x in range(0,4)] 
    annot_texts = ['Goles', 'xG', 'Tiros', 'xG/tiro']
    annot_stats = [data[data['eventType'] == 'Goal'].shape[0], round(data.expectedGoals.sum(), 2), data.shape[0], round(data['expectedGoals'].sum()/data.shape[0],2)]
    for x,s,stat in zip(annot_x, annot_texts, annot_stats):
        hex_annotation = RegularPolygon((x, 70), numVertices=6, radius=4.5, edgecolor='black', fc='None', hatch='.........', lw=1.25)
        ax.add_patch(hex_annotation)
        ax.annotate(
            xy=(x,70),
            text=s,
            xytext=(0,-35),
            textcoords='offset points',
            size=10,
            ha='center',
            va='center'
        )
        if isinstance(stat, int):
            text_stat = f'{stat:.0f}'
        else:
            text_stat = f'{stat:.2f}'
        text_ = ax.annotate(
            xy=(x,70),
            text=text_stat,
            xytext=(0,0),
            textcoords='offset points',
            size=15,
            ha='center',
            va='center',
            weight='bold'
        )
        text_.set_path_effects(
            [path_effects.Stroke(linewidth=1.5, foreground='#efe9e6'), path_effects.Normal()]
        )

    # Draw the annotations at the top of the box.
    median_annotation = ax.annotate(
        xy=(34,109),
        xytext=(x_circle[-1], 109),
        text=f"{((105 - data['x'].median())*18)/16.5:.1f} m.",
        fontproperties = font_normal.prop,
        size=10,
        color='red',
        ha='right',
        va='center',
        arrowprops=dict(arrowstyle= '<|-, head_width=0.35, head_length=0.65',
            color='red',
            fc='#efe9e6',
            lw=0.75)
    )

    ax.annotate(
        xy=(34,109),
        xytext=(4,0),
        text=f"Distancia mediana de tiros",
        textcoords='offset points',
        fontproperties = font_normal.prop,
        size=10,
        color='red',
        ha='left',
        va='center',
        alpha=0.5
    )

    ax.annotate(
        xy=(34,116),
        text=f"{data['playerName'].iloc[0].upper()} - {team_name.upper()}",
        fontproperties = title.prop,
        size=12,
        color='black',
        ha='center',
        va='center',
        weight='bold'
    )
    
    if credit_extra:
        credit_extra = f" por {credit_extra}, "
    else:
        credit_extra = ''
    
    ax.annotate(
        xy=(34,112.5),
        text=f"Tiros sin contar penales realizados en la {league} {season}\nVisualización{credit_extra}de la líbreria de LanusStats.",
        fontproperties = font_normal.prop,
        size=8,
        color='grey',
        ha='center',
        va='center'
    )

    ax_size = 0.1
    image_ax = fig.add_axes(
        [0.75,0.75, ax_size, ax_size],
        fc='None'
    )
    fotmob_url = 'https://images.fotmob.com/image_resources/logo/teamlogo/'
    club_icon = Image.open(urllib.request.urlopen(f'{fotmob_url}{team_id}.png'))
    image_ax.imshow(club_icon)
    image_ax.axis('off')
    text_length = len(data['playerName'].iloc[0].upper()) + len(team_name.upper())
    position_adjustment = text_length * 0.0035
    ax_size = 0.04
    image_ax_position = [0.36 - position_adjustment, 0.84, ax_size, ax_size]
    image_ax = fig.add_axes(
        image_ax_position,
        fc='None'
    )
    fotmob_url = 'https://images.fotmob.com/image_resources/playerimages/'
    club_icon = Image.open(urllib.request.urlopen(f'{fotmob_url}{player_id}.png'))
    image_ax.imshow(club_icon)
    image_ax.axis('off')

    if save_fig:
        plt.savefig(f"{data['playerName'].iloc[0]} hexbix plot.png", dpi=300, bbox_inches='tight')

def threesixfivescores_match_shotmap(match_url, save_fig=False):
    """Makes a shotmap with a URL match from 365Scores

    Args:
        match_url (str): 365Scores match URL. Example: https://www.365scores.com/es-mx/football/match/copa-de-la-liga-profesional-7214/lanus-union-santa-fe-869-7206-7214#id=4033824
        save_fig (bool, optional): Saves the image to a png. Defaults to False.
    """
    
    shotmap = threesixfivescores.get_match_shotmap(match_url)
    home_data, away_data = threesixfivescores.get_team_data(match_url)
    
    color_local, color_visit = home_data['color'], away_data['color']
    local, visit = home_data['name'], away_data['name']
    
    fig, ax = plt.subplots()
    pitch = Pitch(
        pitch_type='opta',
        goal_type='box'
    )

    pitch.draw(ax=ax)

    comp1, comp2 = shotmap[(shotmap['competitorNum'] == 1) & (shotmap['shot_outcome'] != 'Gol')], shotmap[(shotmap['competitorNum'] != 1) & (shotmap['shot_outcome'] != 'Gol')]
    gol_comp_1, gol_comp_2 = shotmap[(shotmap['competitorNum'] == 1) & (shotmap['shot_outcome'] == 'Gol')], shotmap[(shotmap['competitorNum'] != 1) & (shotmap['shot_outcome'] == 'Gol')]
    
    #I need to flip the local shots to make them in the other half
    comp1['side'], comp1['line'] = 100 - comp1['side'], 100 - comp1['line']
    gol_comp_1['side'], gol_comp_1['line'] = 100 - gol_comp_1['side'], 100 - gol_comp_1['line']

    scatter1 = pitch.scatter(comp1.side, comp1.line, s=comp1.xg*500, c=color_local, alpha = .95, edgecolor='black', ax=ax, label='Disparo')
    scatter2 = pitch.scatter(comp2.side, comp2.line, s=comp2.xg*500, c=color_visit, alpha = .95, edgecolor='black', ax=ax)
    scatter3 = pitch.scatter(gol_comp_1.side, gol_comp_1.line, s=gol_comp_1.xg*500, marker='football', ax=ax, label='Gol')
    scatter4 = pitch.scatter(gol_comp_2.side, gol_comp_2.line, s=gol_comp_2.xg*500, marker='football', ax=ax, label='Gol')
    handles = []
    labels = []

    #I made the legend of "Gol" appear only when there is one and if both teams score, only one shows up
    handles.append(scatter1)
    labels.append('Disparo')
    if len(gol_comp_1) > 0:
        handles.append(scatter3)
        labels.append('Gol')

    if len(gol_comp_2) > 0 and len(gol_comp_1) == 0:
        handles.append(scatter4)
        labels.append('Gol')

    plt.legend(handles, labels, loc='lower center', ncol=2)
    plt.title(f'Mapa de tiros de {local} vs. {visit}', fontsize=12)
    
    if save_fig:
        plt.savefig(f'Mapa de tiros de {local} vs. {visit}', bbox_inches='tight', dpi=300)
    
def transfermarkt_player_market_value(transfermarkt_player_id, save_fig=False, plot_age=False):
    values = transfermarkt.get_player_market_value(transfermarkt_player_id)
    values['y'] = values['y'] / 1000000
    x = pd.to_datetime(values.datum_mw, format='%d/%m/%Y')
    y = values.y

    images = list(values['wappen'])
    fig, ax = plt.subplots(figsize = (20,12))
    ax.plot(x,y, ls=':', lw=2, color='black')

    for x0, y0, file in zip(x, y, images):
        ab = AnnotationBbox(OffsetImage(Image.open(urlopen(file))), (x0, y0), frameon=False)
        ax.add_artist(ab)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(1.5)
    values_describe = values['y'].describe()
    if plot_age:
        for i, txt in enumerate(values['age']):
            ax.annotate(f'Edad: {txt}', (x[i], y[i]+((values_describe['max'] - values_describe['min']) / 17.5)), ha='center', size=15)
        
    plt.xticks(size=15)
    plt.yticks(size=15)
    ax.set_ylim(values_describe['min']-6, values_describe['max']+(values_describe['max']*.1))
    plt.ylabel('Valor en Millones de Euros', size=15)
    player_name = values['player'].unique()[0]
    plt.title(f'Valor de mercado de {player_name} a lo largo de su carrera. Fuente: Transfermarkt', size=20, pad=25)
    if save_fig:
        plt.savefig(f'{player_name} market value.png', bbox_inches='tight', dpi=300)