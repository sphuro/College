#include <ncurses.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>

#define ROWS 6
#define COLS 7
#define MAX_TASKS 10
#define TASK_SIZE 100

// Calendar and to-do list data structures
int month[ROWS][COLS];
char tasks[31][MAX_TASKS][TASK_SIZE];
int day, monthIndex, year;

// Function to get the number of days in a month
int getDaysInMonth(int month, int year) {
    switch (month) {
        case 4: case 6: case 9: case 11: return 30;
        case 2:
            return (year % 4 == 0 && (year % 100 != 0 || year % 400 == 0)) ? 29 : 28;
        default: return 31;
    }
}

// Window pointers for ncurses panels
WINDOW *calendarWin;
WINDOW *todoWin;

// Initialize ncurses windows
void initWindows() {
    int termWidth, termHeight;
    getmaxyx(stdscr, termHeight, termWidth);

    int calendarWidth = termWidth * 2 / 3;
    int todoWidth = termWidth - calendarWidth;

    calendarWin = newwin(termHeight, calendarWidth, 0, 0);
    todoWin = newwin(termHeight, todoWidth, 0, calendarWidth);

    box(calendarWin, 0, 0);
    box(todoWin, 0, 0);
}

// Print the calendar for the current month
void printCalendar(WINDOW *win) {
    int daysInMonth = getDaysInMonth(monthIndex + 1, year);
    struct tm timeinfo = {0};
    timeinfo.tm_year = year - 1900;
    timeinfo.tm_mon = monthIndex;
    timeinfo.tm_mday = 1;
    mktime(&timeinfo); // Normalize the structure

    int dayOfWeek = timeinfo.tm_wday;  // Day of the week for the 1st

    wclear(win);
    box(win, 0, 0);
    mvwprintw(win, 1, 2, " Calendar for %02d/%d ", monthIndex + 1, year);
    mvwprintw(win, 2, 2, " Su Mo Tu We Th Fr Sa ");

    int row = 3, col = 2, date = 1;
    while (date <= daysInMonth) {
        wmove(win, row, col);
        for (int i = 0; i < 7; ++i) {
            if (date > daysInMonth) break;
            if (row == 3 && i < dayOfWeek) {
                wprintw(win, "   ");
            } else {
                if (date == day) wattron(win, A_REVERSE); // Highlight current day
                wprintw(win, " %2d", date);
                wattroff(win, A_REVERSE);
                date++;
            }
            col += 3;
        }
        row++;
        col = 2;
    }
    wrefresh(win);
}

// Print the to-do list for the current day
void printTodoList(WINDOW *win) {
    wclear(win);
    box(win, 0, 0);
    mvwprintw(win, 1, 2, " Todo List for %02d/%02d/%d ", day, monthIndex + 1, year);

    for (int i = 0; i < MAX_TASKS && tasks[day - 1][i][0] != '\0'; i++) {
        mvwprintw(win, i + 2, 2, "%d. %s", i + 1, tasks[day - 1][i]);
    }
    wrefresh(win);
}

// Load tasks from a file
void loadTasks() {
    FILE *file = fopen("todolist.txt", "r");
    if (!file) return;

    int fileDay, fileMonth, fileYear;
    char buffer[TASK_SIZE];
    while (fscanf(file, "%d/%d/%d", &fileDay, &fileMonth, &fileYear) == 3) {
        int taskIndex = 0;
        fgetc(file);
        while (fgets(buffer, TASK_SIZE, file)) {
            if (buffer[0] == '\n') break;
            strcpy(tasks[fileDay - 1][taskIndex++], buffer);
        }
    }
    fclose(file);
}

// Save tasks to a file
void saveTasks() {
    FILE *file = fopen("todolist.txt", "w");
    for (int i = 0; i < 31; i++) {
        for (int j = 0; j < MAX_TASKS && tasks[i][j][0] != '\0'; j++) {
            fprintf(file, "%02d/%02d/%d\n", i + 1, monthIndex + 1, year);
            fprintf(file, "%s", tasks[i][j]);
            fprintf(file, "\n");
        }
    }
    fclose(file);
}

// Edit the to-do list interactively
void editTodoList() {
    echo();
    char newTask[TASK_SIZE];
    int taskIndex = 0;

    wclear(todoWin);
    box(todoWin, 0, 0);
    mvwprintw(todoWin, 1, 2, "Edit Todo List for %02d/%02d/%d:", day, monthIndex + 1, year);

    for (int i = 0; i < MAX_TASKS && tasks[day - 1][i][0] != '\0'; i++) {
        mvwprintw(todoWin, i + 2, 2, "%d. %s", i + 1, tasks[day - 1][i]);
        taskIndex++;
    }

    mvwprintw(todoWin, taskIndex + 2, 2, "New task (leave blank to finish):");
    while (taskIndex < MAX_TASKS) {
        mvwprintw(todoWin, taskIndex + 3, 2, "%d: ", taskIndex + 1);
        wrefresh(todoWin);
        wgetnstr(todoWin, newTask, TASK_SIZE);
        if (newTask[0] == '\0') break;
        strcpy(tasks[day - 1][taskIndex++], newTask);
    }

    saveTasks();
    noecho();
}

// Navigate calendar with arrow keys
void navigateCalendar() {
    int ch;
    int daysInMonth = getDaysInMonth(monthIndex + 1, year);
    keypad(stdscr, TRUE);

    while (1) {
        printCalendar(calendarWin);
        printTodoList(todoWin);

        ch = wgetch(calendarWin);
        switch (ch) {
            case 'h': if (day > 1) day--; break;
            case 'l': if (day < daysInMonth) day++; break;
            case 'j': if (day + 7 <= daysInMonth) day += 7; else day = daysInMonth; break;
            case 'k': if (day - 7 > 0) day -= 7; else day = 1; break;
            case 'n': monthIndex = (monthIndex + 1) % 12; day = 1; break;
            case 'p': monthIndex = (monthIndex == 0) ? 11 : monthIndex - 1; day = 1; break;
            case '\n': editTodoList(); break;
            case 'q': return;
        }
    }
}

void initializeWithCurrentDate() {
    time_t t = time(NULL);
    struct tm *currentTime = localtime(&t);
    day = currentTime->tm_mday;
    monthIndex = currentTime->tm_mon;
    year = currentTime->tm_year + 1900;
}

int main() {
    initscr();
    cbreak();
    noecho();
    start_color();
    init_pair(1, COLOR_GREEN, COLOR_BLACK);

    initWindows();
    loadTasks();

    initializeWithCurrentDate();
    navigateCalendar();

    delwin(calendarWin);
    delwin(todoWin);
    endwin();

    return 0;
}

