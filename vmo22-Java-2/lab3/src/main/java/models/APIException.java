package models;

public class APIException {
    public String message;
    public int code;

    public APIException(String message, int code) {
        this.message = message;
        this.code = code;
    }
}
