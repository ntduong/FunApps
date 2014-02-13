/**
    Simple ASCII Snake-Eat-Food Game with naive AI.
    Ver 0.0

    Written by Duong Nguyen
    Email:ntduong268(@)gmail.com
*/

#include<iostream>
#include<algorithm>
#include<string>
#include<deque>
#include<vector>
#include<fstream>
#include<ctime>
#include<cstdlib>
#include<cassert>

using namespace std;

#define DEBUG 0


/************************
*  Constants definition *
************************/
// Amount of food to be eaten to win
const int MAX_EAT_FOOD = 20;

// Tile types
const char EMPTY_T = ' ';
const char FOOD_T = '$';
const char SNAKE_T = '*';
const char WALL_T = '#';

// Misc
const double WAIT_TIME = 0.1;
const double RANDOM_TURN_PROB = 0.1;
const string WIN_CLEAR_CMD = "CLS";
const string UNIX_CLEAR_CMD = "clear";
const int DEFAULT_NROWS = 20;
const int DEFAULT_NCOLS = 20;

/*******************
*  Data structure  *
*******************/
struct Cell{
    int row, col;
};

struct Game{
    vector<string> world;
    int n_rows, n_cols;
    deque<Cell> snake;
    int dc, dr;
    int n_eaten;
};

void random_init_game(Game& m_Game, int n_rows, int n_cols, int n_foods=10, int n_walls=10){

    m_Game.n_rows = n_rows;
    m_Game.n_cols = n_cols;
    m_Game.n_eaten = 0;
    m_Game.dc = 0;
    m_Game.dr = 1;

    string fence = string(n_cols, WALL_T);
    string normal_row = "#" + string(n_cols-2, EMPTY_T) + "#";

    m_Game.world.push_back(fence);
    for(int r = 1; r <= n_rows-2; r++){
        m_Game.world.push_back(normal_row);
    }
    m_Game.world.push_back(fence);

    // Put foods;
    while(n_foods--){
        int food_r = rand() % (n_rows-2) + 1 ;
        int food_c = rand() % (n_cols-2) + 1;

        assert(m_Game.world[food_r][food_c] == EMPTY_T);
        m_Game.world[food_r][food_c] = FOOD_T;
    }

    // Put snake
    while(1){
        int snake_r = rand() % (n_rows-2) + 1;
        int snake_c = rand() % (n_cols-2) + 1;
        if(m_Game.world[snake_r][snake_c] == EMPTY_T){
            m_Game.world[snake_r][snake_c] = SNAKE_T;
            m_Game.snake.push_back((Cell){snake_r, snake_c});
            break;
        }
    }

    // Add some extra walls
    if(n_walls > 0){
        int max_trial = n_walls * 4;
        while(1){
            if((n_walls == 0) || (max_trial == 0)) break;

            max_trial--;
            int r = rand() % (n_rows-2) + 1;
            int c = rand() % (n_cols-2) + 1;

            if(m_Game.world[r][c] == EMPTY_T){
                m_Game.world[r][c] = WALL_T;
                n_walls--;
            }
        }
    }
}

void init_game_from_file(Game& m_Game, const string& fname="level.txt"){

    ifstream fin(fname.c_str());
    if(!fin.is_open()){
        cerr << "Could not load game file!";
        exit(1);
    }

    fin >> m_Game.n_rows >> m_Game.n_cols; // world size
    fin >> m_Game.dc >> m_Game.dr; // initial snake direction

    string line;
    getline(fin, line); // discard any newline left in the stream

    for(int r = 0; r < m_Game.n_rows; r++){
        getline(fin, line);

#if DEBUG
        cout << line << endl;
        assert(line.length() == m_Game.n_cols)
#endif
        m_Game.world.push_back(line);
        for(int c = 0; c < m_Game.n_cols; c++){
            if(line[c] == SNAKE_T){
                m_Game.snake.push_back((Cell){r,c});
            }
        }
    }

    m_Game.n_eaten = 0;
    fin.close();
}

// Print out input for debugging purpose
void logging(const Game& m_Game){

    cout << m_Game.n_rows << " " << m_Game.n_cols << endl;
    cout << m_Game.dc << " " << m_Game.dr << endl;
    for(auto s : m_Game.world){
        cout << s << endl;
    }
    cout << m_Game.n_eaten << endl;

    cout << "Inital snake position: ";
    assert(m_Game.snake.size() == 1); // Initially snake is one cell
    for(auto i : m_Game.snake){
        cout << "{" << i.row << ", " << i.col << "}" << endl;
    }
}

// Temporarily pause game for a while
void pause(double wait_time=WAIT_TIME){

    clock_t start_time = clock();
    while(static_cast<double>((clock()-start_time))/CLOCKS_PER_SEC < wait_time);
}

// Print out game status at given step
void show_world(const Game& m_Game){

    //First, clear screen for clean view :)
    system(WIN_CLEAR_CMD.c_str());

    for(auto line : m_Game.world){
        cout << line << endl;
    }
    cout << "Food eaten: " << m_Game.n_eaten << endl;
}

void show_result(const Game& m_Game){

    show_world(m_Game);
    if(m_Game.n_eaten == MAX_EAT_FOOD) {
        cout << "ENOUGH FOOD AND WIN\n";
    } else{
        cout << "CRASHED!!!\n";
    }
}

// Get the next position for snake head in given direction (dc, dr)
Cell get_next_head_pos(const Game& m_Game, int dc, int dr){

    Cell new_pos = m_Game.snake.front();
    new_pos.row += dr;
    new_pos.col += dc;
    return new_pos;
}

// Check if given cell (r,c) is safe to move in
bool is_safe(const Game& m_Game, int r, int c){
    int n_rows = m_Game.n_rows, n_cols = m_Game.n_cols;

    if((r < 0) || (r >= n_rows) || (c < 0) || (c >= n_cols))
        return false;

    char tile = m_Game.world[r][c];
    if((tile == WALL_T) || (tile == SNAKE_T))
        return false;

    return true;
}

// True means selecting 1st choice
bool random_select(double prob=RANDOM_TURN_PROB){
    return rand()/(RAND_MAX+1.0) < prob;
}

// Decide direction to move next, update Game direction
void choose_next_dir(Game& m_Game){

    Cell cur_head = m_Game.snake.front();
    // if can not move by current direction or we decide to turn
    if(!is_safe(m_Game, cur_head.row+m_Game.dr, cur_head.col+m_Game.dc) || random_select(RANDOM_TURN_PROB)) {

        int dc_left = -m_Game.dr, dr_left = m_Game.dc; // left dir
        int dc_right = m_Game.dr, dr_right = -m_Game.dc; // right dir

        bool left_safe = is_safe(m_Game, cur_head.row+dr_left, cur_head.col+dc_left);
        bool right_safe = is_safe(m_Game, cur_head.row+dr_right, cur_head.col+dc_right);

        bool turn_left = false;
        if(!left_safe && !right_safe){ // can not turn both left and right
            return;
        } else if(left_safe && !right_safe){ // can only turn left
            turn_left = true;
        } else if(left_safe && right_safe){ // can turn left &  right
            turn_left = random_select(0.5); // randomly select direction
        }

    #if DEBUG
        if(turn_left) cout << "TURN LEFT\n";
    #endif // DEBUG

        // Update next direction
        m_Game.dc = turn_left ? dc_left : dc_right;
        m_Game.dr = turn_left ? dr_left : dr_right;
    }
}

// Put new food if snake ate one food
void put_new_food(Game& m_Game){
    while(1){
        int r = rand() % m_Game.n_rows;
        int c = rand() % m_Game.n_cols;
        if(m_Game.world[r][c] == EMPTY_T){
            m_Game.world[r][c] = FOOD_T;
            break;
        }
    }
}

// Move snake AFTER choosing direction
bool make_move(Game& m_Game){

    Cell new_head = get_next_head_pos(m_Game, m_Game.dc, m_Game.dr);
    if(!is_safe(m_Game, new_head.row, new_head.col)) {
       return false; // can not move
    }

    int new_r = new_head.row, new_c = new_head.col;
    // If the cell is food, eat it and randomly place new food
    // Note that, after eating the snake grow up by one cell
    if(m_Game.world[new_r][new_c] == FOOD_T){
        m_Game.n_eaten++;
        put_new_food(m_Game);
    } else{
        Cell cur_tail = m_Game.snake.back();
        m_Game.world[cur_tail.row][cur_tail.col] = EMPTY_T;
        m_Game.snake.pop_back();
    }

    // new head
    m_Game.world[new_r][new_c] = SNAKE_T;
    m_Game.snake.push_front(new_head);

    return true;
}

void sim(Game& m_Game){

    while(m_Game.n_eaten < MAX_EAT_FOOD){
        // show the current status
        show_world(m_Game);

        // select next direction and update game
        choose_next_dir(m_Game);
        if(!make_move(m_Game)){
            break;
        }
        pause();
    }

    // Show final result
    show_result(m_Game);
}

void play_game(){

    int type;
    while(1){
        cout << "Choose game type (0 - random game, 1 - loading from file): ";
        cin >> type;
        if(type == 0 || type == 1) break;
        else {
            cout << "Try again!\n";
        }
    }

    // seed random generator
    srand(static_cast<unsigned>(time(NULL)));
    Game* m_Game = new Game();
    if(type == 0){
        random_init_game(*m_Game, DEFAULT_NROWS, DEFAULT_NCOLS);
    } else{
        assert(type == 1);
        init_game_from_file(*m_Game, "level.txt");
    }

#if DEBUG
    logging(*m_Game);
#endif // DEBUG

    sim(*m_Game);

    cout << "GOODBYE!\n";

    delete m_Game;
    m_Game = NULL;
}

int main(){
    play_game();
    return 0;
}
