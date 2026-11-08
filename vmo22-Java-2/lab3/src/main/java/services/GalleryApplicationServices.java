package services;

import models.APIException;
import models.schemas.Picture;
import models.schemas.PictureCreate;
import views.ASResponse;

import javax.servlet.http.HttpSession;
import java.util.ArrayList;
import java.util.UUID;

public class GalleryApplicationServices {


    public static ASResponse<Picture, APIException> createPicture(PictureCreate data, PictureRepo repo) {
        if (data.filename == null || data.filename.isEmpty()) {
            return new ASResponse<>(null, new APIException("Имя файла не может быть пустым ", 400));
        }

        if (data.size == null || data.size <= 0) {
            return new ASResponse<>(null, new APIException("Инвалидный размер файла", 400));
        }

        Picture picture;
        try {
            picture = repo.createPicture(data.filename, data.size);
        } catch (Exception error) {
            return new ASResponse<>(null, new APIException("Ошибка сервера", 500));
        }
        return new ASResponse<>(picture, null);
    }

    public static ASResponse<ArrayList<Picture>, APIException> listOfPictures(PictureRepo repo, String orderBy) {
        ArrayList<Picture> pictures = repo.get_all();
        // Так как БД не находится удаленно, то нет смысла описывать логику сортировки на стороне БД

        if (orderBy != null && orderBy.equals("size")) {
            pictures.sort((a, b) -> a.size - b.size);
        } else if (orderBy != null && orderBy.equals("filename")) {
            pictures.sort((a, b) -> a.filename.compareTo(b.filename));
        } else if (orderBy != null && orderBy.equals("created_at")) {
            pictures.sort((a, b) -> a.created_at.compareTo(b.created_at));
        }
        return new ASResponse<>(pictures, null);
    }

    public static ASResponse<Picture, APIException> deletePicture(UUID id, PictureRepo pictureRepo) {
        if (pictureRepo.get(id) == null) {
            return new ASResponse<>(null, new APIException("Изображение не найдено", 404));
        }

        try {
            pictureRepo.delete(id);
        } catch (Exception error) {
            return new ASResponse<>(null, new APIException("Ошибка сервера", 500));
        }
        return new ASResponse<>(null, null);
    }
}
