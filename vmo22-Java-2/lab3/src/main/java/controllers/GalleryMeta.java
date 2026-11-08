package controllers;

import com.fasterxml.jackson.databind.ObjectMapper;
import models.APIException;
import models.schemas.PictureCreate;
import services.GalleryApplicationServices;
import views.ASResponse;
import models.schemas.Picture;
import services.PictureRepo;

import java.io.*;
import java.util.ArrayList;
import javax.servlet.http.*;
import javax.servlet.annotation.*;

@WebServlet(name = "GalleryMeta", value = "/api/gallery")
public class GalleryMeta extends HttpServlet {

    PictureRepo pictureRepo;

    public void init() {
        // Это должно быть в глобал скоупе, но я не знаю как это сделать

        pictureRepo = new PictureRepo(new File("/home/jkearnsl/IdeaProjects/lab3/gallerydb.xml"));

    }

    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        // Pre-process
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");
        HttpSession session = request.getSession();
        String orderBy = request.getParameter("orderBy");

        // Process
        ASResponse<ArrayList<Picture>, APIException> resp = GalleryApplicationServices.listOfPictures(
                pictureRepo,
                orderBy
        );


        // Post-Process
        if (resp.exception != null) {
            response.setStatus(resp.exception.code);
        }
        ObjectMapper objectMapper = new ObjectMapper();
        String jsonString = objectMapper.writeValueAsString(resp);
        PrintWriter out = response.getWriter();
        out.print(jsonString);
        out.flush();
        out.close();
    }

    public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
        // Pre-process
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");

        // Process
        ASResponse<Picture, APIException> resp = GalleryApplicationServices.createPicture(
                new PictureCreate(
                        request.getParameter("filename"),
                        Integer.parseInt(request.getParameter("size"))
                ),
                pictureRepo
        );

        // Post-Process
        if (resp.exception != null) {
            response.setStatus(resp.exception.code);
        }
        ObjectMapper objectMapper = new ObjectMapper();
        String jsonString = objectMapper.writeValueAsString(resp);
        PrintWriter out = response.getWriter();
        out.print(jsonString);
        out.flush();
        out.close();
    }

    public void doDelete(HttpServletRequest request, HttpServletResponse response) throws IOException {
        // Pre-process
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");

        // Process
        ASResponse<Picture, APIException> resp = GalleryApplicationServices.deletePicture(
                java.util.UUID.fromString(request.getParameter("id")),
                pictureRepo
        );

        // Post-Process
        if (resp.exception != null) {
            response.setStatus(resp.exception.code);
        }
        ObjectMapper objectMapper = new ObjectMapper();
        String jsonString = objectMapper.writeValueAsString(resp);
        PrintWriter out = response.getWriter();
        out.print(jsonString);
        out.flush();
        out.close();
    }
}