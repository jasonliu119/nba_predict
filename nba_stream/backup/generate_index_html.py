import os.path
import datetime
import sys

HOME_DIR = '/home/weijie/'

class Game:
    def __init__(self):
        self.away = ''
        self.home = ''
        self.time = ''
        self.links = {}

    def __str__(self):
        return "asway {}, home {}, time {}, link {}".format(self.away, self.home, self.time, str(self.links))

def normalize_link_text(text, k):
    words = [
        'boston', 'brooklyn', 'york', 'philadelphia', 'toronto',
        'golden','clipper','laker','Phoenix','Sacramento',
        'chicago','Cleveland','Detroit','Indiana','Milwaukee',
        'Atlanta','Charlotte', 'miami','orlando','washington',
        'denver','minnesota','Oklahoma','Portland','Utah',
        'Dallas','houston','Memphis','Orleans','Antonio',
        'Celtic', 'Net', 'Knick', '76er', 'Raptor',
        'Warrior','clipper','laker','Sun','King',
        'Bull','Cavalier','Piston','Pacer','Buck',
        'Hawk','Hornet', 'Heat','Magic','Wizard',
        'Nugget','Timberwol','Thunder','Blazer','Jazz',
        'Maverick','Rocket','Grizzl','Pelican','Spur']
    has_word = False
    for word in words:
        if word in text:
            has_word = True
            break
    if has_word:
        text = "Web Stream"
    return 'Link {}: '.format(k) + text

def populate_game_links(game, link_file_path, init_k):
    if os.path.isfile(link_file_path):
        with open(link_file_path, 'r') as link_file:
            link_lines = link_file.readlines()
        j = 0
        k = init_k
        while j < len(link_lines):
            text = link_lines[j]
            j += 1
            link = link_lines[j]
            j += 1
            text = normalize_link_text(text, k)
            game.links[text] = link
            k += 1
        return k
    return init_k

def read_today_and_parse(file):
    '''
    live
    12
    05
    1545436800

    live
    13
    17
    1545436800

    live
    16
    03
    1545438600

    '''
    lines = []
    with open(file, 'r') as f:
        lines = f.readlines()
    ret = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line != "live":
            i = i + 1
            continue
        game = Game()
        game.links.clear()

        team_list = []
        i = i + 1
        game.away = lines[i].strip()
        team_list.append(int(game.away))
        i = i + 1
        game.home = lines[i].strip()
        team_list.append(int(game.home))
        i = i + 1
        game.time = lines[i].strip()
        i = i + 1

        now = datetime.datetime.now()
        small = str(min(team_list))
        big = str(max(team_list))
        if len(small) == 1:
            small = '0' + small
        if len(big) == 1:
            big = '0' + big
        reddit_link_file_path = HOME_DIR + "/nba/game_links/{}/{}-{}.txt".format(now.strftime("%Y-%m-%d"), small, big)
        nba_streams_link_file_path = HOME_DIR + "/nba/game_links/{}/b-{}-{}.txt".format(now.strftime("%Y-%m-%d"), small, big)

        print "nba_streams_link_file_path: " + nba_streams_link_file_path

        init_k = 1 # means the number of the next link
        init_k |= populate_game_links(game, reddit_link_file_path, init_k)
        init_k |= populate_game_links(game, nba_streams_link_file_path, init_k)
        if init_k == 1:
            game.links['Appears before game starts'] = ''

        print (" -- game is: " + str(game))
        ret.append(game)

    return ret

def generate_img_html(team):
    return "<img src=\"/static/{}.png\" alt=\"nba\" width=\"100\" height=\"100\" style=\"border:20px solid white;\">".format(team)

def generate_links_html(game):
    html = '<br>'
    titles = game.links.keys()
    if len(titles) == 0:
        html += "<div class=\"game_link\"><a href=\"{}\">{}</a><br>".format("", 
            "No links found. Game may have ended.")
        html += "<br>"
    else:
        titles.sort()

    for title in titles:
        html += "<div class=\"game_link\"><a href=\"{}\">{}</a><br>".format(game.links[title], title)
        html += "<br>"

    html += "<h4><div class=\"game_time\">{}</div></h4></div>".format(game.time)

    return html

def generate_index_html(directory, index_template, games):
    games_table = ''
    for game in games:

        games_table += '<tr>'
        games_table += '<td align="center">'
        games_table += generate_img_html(game.away)
        games_table += '</td>'

        games_table += '<td align="left">'
        games_table += generate_links_html(game)
        games_table += '</td>'

        games_table += '<td align="center">'
        games_table += generate_img_html(game.home)
        games_table += '</td>'

        games_table += '</tr>'


    html = ''
    with open(directory + "/" + index_template, 'r') as f:
        html = f.read()

    import re
    ret = re.sub('@@@', games_table, html)
    return ret

def main():
    home_dir = HOME_DIR
    if len(sys.argv) > 1:
        home_dir = sys.argv[1]

    print 'main'
    games = read_today_and_parse(HOME_DIR + '/nba/today.txt')
    directory = "./hub/templates/"
    html = generate_index_html(directory, "home.html.template", games)

    with open(directory + "home.html", "wb") as f:
        f.write(html)

if __name__ == '__main__':
    while True:
        try:
            main()
            print "\n ---- updated the html at time {}\n".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            import time
            time.sleep(30 * 10)
        except Exception as e:
            print "Error in generate_index_html: " + str(e.message)


