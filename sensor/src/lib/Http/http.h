#ifndef __HTTP_H
#define __HTTP_H
#include "utils.h"

#define HTTP_V "HTTP/1.1"
#define _HTABLE_SIZE 1024

#define ADD_HEADER(req, name, val) insertHeader(createHeader(name, val),\
                                                req->headers);


#ifdef __cplusplus
extern "C"
{
#endif


  typedef struct Header{
    char name[40];
    char value[50];

    // Linked list ptr's
    struct Header *nxt_ptr;
    struct Header *prev_ptr;
  } Header;

  typedef struct HeaderList{
    int len;
    Header *head;
  } HeaderList;

  Header *createHeader(char *, char *);
  Header *delHeader(Header *header, HeaderList*);

  int insertHeader(Header*, HeaderList*);
  Header *getHeader(HeaderList*, char*);
  
  
  typedef struct Request{
    char method[6];
    char path[60];
    HeaderList *headers;
    char *data;
  } Request;

  Request *createRequest(char*, char*, char*);
  void delRequest(Request*);
  void reqtostr(Request *req, char *dst);

  typedef struct Response{
    int statusCode;
    char statusMsg[20];
    HeaderList *headers;
    char *data;
  } Response;




  
#ifdef __cplusplus
}
#endif
  
#endif
