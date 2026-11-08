package services;

import models.schemas.Picture;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import java.io.File;
import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.Locale;
import java.util.UUID;

public class PictureRepo {

    File filepath;

    public PictureRepo(File filepath) {
        this.filepath = filepath;
    }

    public Picture createPicture(String filename, int size) throws IOException, ParserConfigurationException, SAXException, TransformerException {
        DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
        DocumentBuilder db = dbf.newDocumentBuilder();
        Document doc = db.parse(filepath);

        UUID id = UUID.randomUUID();

        Element root = doc.getDocumentElement();

        // Create new picture element
        Element pictureElement = doc.createElement("picture");
        pictureElement.setAttribute("id", id.toString());

        Element filenameElement = doc.createElement("filename");
        filenameElement.appendChild(doc.createTextNode(filename));
        pictureElement.appendChild(filenameElement);

        Element sizeElement = doc.createElement("size");
        sizeElement.appendChild(doc.createTextNode(Integer.toString(size)));
        pictureElement.appendChild(sizeElement);

        Element createdAtElement = doc.createElement("created_at");
        createdAtElement.appendChild(doc.createTextNode(new Date().toString()));
        pictureElement.appendChild(createdAtElement);

        // Add to root
        root.appendChild(pictureElement);

        // Save
        TransformerFactory transformerFactory = TransformerFactory.newInstance();
        Transformer transformer = transformerFactory.newTransformer();
        DOMSource source = new DOMSource(doc);
        StreamResult result = new StreamResult(filepath);
        transformer.transform(source, result);

        return new Picture(id, filename, size, new Date());
    }

    public Picture get(UUID id) {
        return getBy("id", id);
    }

    public ArrayList<Picture> get_all() {
        ArrayList<Picture> pictures = new ArrayList<>();
        try {
            DocumentBuilder documentBuilder = DocumentBuilderFactory.newInstance().newDocumentBuilder();
            Document document = documentBuilder.parse(filepath);
            SimpleDateFormat format = new SimpleDateFormat("E MMM dd HH:mm:ss z yyyy", Locale.ENGLISH);

            NodeList nodeList = document.getElementsByTagName("picture");

            for (int i = 0; i < nodeList.getLength(); i++) {
                Node node = nodeList.item(i);

                if (node.getNodeType() == Node.ELEMENT_NODE) {
                    Node idNode = node.getAttributes().getNamedItem("id");
                    Node filenameNode = node.getChildNodes().item(0);
                    Node sizeNode = node.getChildNodes().item(1);
                    Node created_atNode = node.getChildNodes().item(2);

                    pictures.add(
                            new Picture(
                                UUID.fromString(idNode.getTextContent()),
                                filenameNode.getTextContent(),
                                Integer.parseInt(sizeNode.getTextContent()),
                                format.parse(created_atNode.getTextContent())
                        )
                    );
                }
            }
        } catch (ParserConfigurationException | IOException | SAXException | ParseException error) {
            throw new RuntimeException(error);
        }
        return pictures;
    }

    private Picture getBy(String key, Object searchValue){
        try {
            DocumentBuilder documentBuilder = DocumentBuilderFactory.newInstance().newDocumentBuilder();
            Document document = documentBuilder.parse(filepath);
            SimpleDateFormat format = new SimpleDateFormat("E MMM dd HH:mm:ss z yyyy", Locale.ENGLISH);
            NodeList nodeList = document.getElementsByTagName("picture");

            for (int i = 0; i < nodeList.getLength(); i++) {
                Node node = nodeList.item(i);

                if (node.getNodeType() == Node.ELEMENT_NODE) {
                    Node keyNode = node.getChildNodes().item(0);

                    boolean isInNodeName = (
                            keyNode.getNodeName().equals(key) &&
                            keyNode.getTextContent().equals(searchValue.toString())
                    );
                    boolean isInNodeAttributes = (
                            node.getAttributes().getNamedItem(key) != null &&
                            node.getAttributes().getNamedItem(key).getTextContent().equals(searchValue.toString())
                    );

                    if (isInNodeName || isInNodeAttributes) {
                        Node idNode = node.getAttributes().getNamedItem("id");
                        Node filenameNode = node.getChildNodes().item(0);
                        Node sizeNode = node.getChildNodes().item(1);
                        Node created_atNode = node.getChildNodes().item(2);

                        return new Picture(
                                UUID.fromString(idNode.getTextContent()),
                                filenameNode.getTextContent(),
                                Integer.parseInt(sizeNode.getTextContent()),
                                format.parse(created_atNode.getTextContent())
                        );
                    }
                }
            }
        } catch (ParserConfigurationException | SAXException | IOException | ParseException error) {
            throw new RuntimeException(error);
        }
        return null;
    }

    public void delete(UUID id) {
        DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
        try {
            DocumentBuilder db = dbf.newDocumentBuilder();
            Document doc = db.parse(filepath);


            Element root = doc.getDocumentElement();

            NodeList nodeList = doc.getElementsByTagName("picture");
            for (int i = 0; i < nodeList.getLength(); i++) {
                Node node = nodeList.item(i);
                Node idNode = node.getAttributes().getNamedItem("id");
                if (idNode.getTextContent().equals(id.toString())) {
                    root.removeChild(node);
                }
            }

            // Save
            TransformerFactory transformerFactory = TransformerFactory.newInstance();
            Transformer transformer = transformerFactory.newTransformer();
            DOMSource source = new DOMSource(doc);
            StreamResult result = new StreamResult(filepath);
            transformer.transform(source, result);


    } catch (ParserConfigurationException | TransformerException | IOException | SAXException e) {
            throw new RuntimeException(e);
        }
    }
}
