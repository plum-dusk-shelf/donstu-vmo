package views;

import models.APIException;

public class ASResponse<ResponseModel, T extends APIException> {
    public ResponseModel data;
    public T exception;

    public ASResponse(ResponseModel data, T exception) {
        this.data = data;
        this.exception = exception;
    }
}
