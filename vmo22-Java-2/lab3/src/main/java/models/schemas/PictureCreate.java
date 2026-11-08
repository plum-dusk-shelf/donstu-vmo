package models.schemas;

public class PictureCreate {
    public String filename;
    public Integer size;

    public PictureCreate(String filename, Integer size) {
        this.filename = filename;
        this.size = size;
    }
}
