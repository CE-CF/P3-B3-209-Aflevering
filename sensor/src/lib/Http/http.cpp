#include "http.h"
#include <cstddef>
#include <cstdlib>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <Arduino.h>

#ifdef __cplusplus
extern "C"
{
#endif

  Header *createHeader(char *name, char *val){
    Header *hd = (Header*) malloc(sizeof(Header));
    if (hd != NULL) {
      memcpy(hd->name, name, strlen(name)+1);
      memcpy(hd->value, val, strlen(val)+1);
      hd->nxt_ptr = NULL;
      hd->prev_ptr = NULL;
      return hd;
    }
    return NULL;
  }

  Header *delHeader(Header *header, HeaderList *s){
    Header *tmp = header->nxt_ptr;
    if (header->nxt_ptr != NULL){
      header->nxt_ptr->prev_ptr = header->prev_ptr;
    }
    if (header->prev_ptr != NULL){
      header->prev_ptr->nxt_ptr = header->nxt_ptr;
    }
    s->len--;
    free(header);
    memset(header, 0, sizeof(Header));
    return tmp;
  }
  
  int insertHeader(Header *header, HeaderList *dst){
    header->nxt_ptr = dst->head;
    if (dst->head != NULL)
      dst->head->prev_ptr = header;
    dst->head = header;
    header->prev_ptr = NULL;
    dst->len += 1;
    return dst->len;
  }
  
  Header *getHeader(HeaderList *src, char *key){
    Header *tmp;
    tmp = src->head;
    while( (strcmp(tmp->name, key) != 0)&& (tmp->nxt_ptr != NULL)){
        tmp = tmp->nxt_ptr;
    }

    return tmp;
  }

  Request *createRequest(char *method, char *path, char *data){
    Request *req;
    req = (Request *) malloc(sizeof(Request));
    memset(req, 0, sizeof(Request));
    req->headers = (HeaderList *)malloc(sizeof(HeaderList));
    memset(req->headers, 0, sizeof(HeaderList));
    memcpy(req->method, method, sizeof(method));
    memcpy(req->path, path, strlen(path) +1);

    int dataLen = strlen(data);
    req->data = data;

    char str[10];
    sprintf(str, "%d", dataLen);
    ADD_HEADER(req, "Content-length", str)

    return req;
  }

  void delRequest(Request *req){
    Header *tmp = req->headers->head;
    for(int i = 0; i < req->headers->len; i++){
      tmp = delHeader(tmp, req->headers);
    }
    delHeader(tmp, req->headers);
    // Free everything
    free(req->headers);
    free(req);

    // Set everything to 0
    memset(req->headers, 0, sizeof(HeaderList));
    memset(req, 0, sizeof(Request));
  }
  
  void reqtostr(Request *req, char *dst){
    char headerStr[255];
    memset(headerStr, 0, sizeof(headerStr));
    Header *tmp = req->headers->head;
    for (int i = 0; i < req->headers->len; i++){
      if (strcmp(tmp->name, "Host") != 0){
        strcat(headerStr, tmp->name);
        strcat(headerStr, ": ");
        strcat(headerStr, tmp->value);
        strcat(headerStr, "\r\n");
      }
      tmp = tmp->nxt_ptr;
      if (tmp == NULL)
        break;
    }

    sprintf(dst,
            "%s %s " HTTP_V "\r\n" // METHOD PATH VERSION
            "Host: %s\r\n"         // Host header, must be first
            "%s\r\n"               // Header string
            "%s",                  // Data
            req->method, req->path,
            getHeader(req->headers, "Host")->value,
            headerStr,
            req->data
            );
  }


  
#ifdef __cplusplus
}
#endif
  
