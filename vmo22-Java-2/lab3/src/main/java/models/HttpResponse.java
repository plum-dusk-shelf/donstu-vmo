package models;


public class HttpResponse {
    public String content;
    public int status;

    public HttpResponse(String content, int status) {
        this.content = content;
        this.status = status;
    }
}
