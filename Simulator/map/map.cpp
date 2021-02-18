#include "map.hpp"

Map::Map(double height, double width, double elementary_size, double center_x, double center_y){
    this->center[0]=center_x;
    this->center[1]=center_y;
    if(elementary_size != 0){
        this->height_indice=(int)height/elementary_size;
        this->width_indice=(int)width/elementary_size;
    }
    
    std::vector<std::vector<int>> map(this->height_indice, std::vector<int> (this->width_indice), 0);
    this->map=map;
}


void Map::print(void){
    for(int i=0; i<this->height_indice; i++){
        for(int j=0; j<this->height_indice; j++){
            std::cout<<this->map[i][j];
        }
        std::cout<<std::endl;
    }
}