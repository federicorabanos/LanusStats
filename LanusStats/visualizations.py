

import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import PyPizza, add_image, FontManager
from PIL import Image
from .exceptions import MatchDoesntHaveInfo
from .fbref import Fbref
from .fotmob import FotMob
fbref, fotmob = Fbref(), FotMob()

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