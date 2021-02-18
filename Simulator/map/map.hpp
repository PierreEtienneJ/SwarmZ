#ifndef MAP_HPP
#define MAP_HPP

#include <iostream>
#include <vector> 

class Map{
    private:
    std::vector<std::vector<int>> map;
    int height_indice;
    int width_indice;
    double elementary_size;
    double center[2];

    public:
    Map(double height, double width, double elementary_size, double center_x, double center_y);
    void print(void);
};

#endif