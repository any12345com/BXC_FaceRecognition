#ifndef BXC_SERVER_H
#define BXC_SERVER_H
class Server
{
public:
    explicit Server();
    ~Server();

public:
    void start(void* arg);

};

void api_index(struct evhttp_request* req, void* arg);
void api_controls(struct evhttp_request* req, void* arg);

void api_control_add(struct evhttp_request* req, void* arg);
void api_control_cancel(struct evhttp_request* req, void* arg);
void parse_get(struct evhttp_request* req, struct evkeyvalq* params);
void parse_post(struct evhttp_request* req, char* buff);

#endif //BXC_SERVER_H

