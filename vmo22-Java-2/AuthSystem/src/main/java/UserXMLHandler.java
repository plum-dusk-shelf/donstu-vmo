package main.java;

import jakarta.xml.bind.JAXBContext;
import jakarta.xml.bind.JAXBException;
import jakarta.xml.bind.Marshaller;
import jakarta.xml.bind.Unmarshaller;
import jakarta.xml.bind.annotation.XmlRootElement;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class UserXMLHandler {
    private static final String FILE_PATH = "C:\\Users\\simafrus\\Java-2\\AuthSystem\\resources\\main\\AuthSystem\\users.xml";
    private List<User> users;

    public UserXMLHandler() {
        users = new ArrayList<>();
        loadUsers();
    }

    @SuppressWarnings("unchecked")
    private void loadUsers() {
        try {
            File file = new File(FILE_PATH);
            if (!file.exists()) {
                file.createNewFile();
                return;
            }

            if (file.length() == 0) {
                return;
            }

            JAXBContext context = JAXBContext.newInstance(UsersWrapper.class);
            Unmarshaller unmarshaller = context.createUnmarshaller();
            UsersWrapper wrapper = (UsersWrapper) unmarshaller.unmarshal(file);
            users = wrapper.getUsers();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void saveUsers() {
        try {
            JAXBContext context = JAXBContext.newInstance(UsersWrapper.class);
            Marshaller marshaller = context.createMarshaller();
            marshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, true);

            UsersWrapper wrapper = new UsersWrapper();
            wrapper.setUsers(users);

            marshaller.marshal(wrapper, new File(FILE_PATH));
        } catch (JAXBException e) {
            e.printStackTrace();
        }
    }

    public void addUser(User user) {
        users.add(user);
        saveUsers();
    }

    public User findUser(String login) {
        for (User user : users) {
            if (user.getLogin().equals(login)) {
                return user;
            }
        }
        return null;
    }

    public boolean userExists(String login) {
        return findUser(login) != null;
    }
}

@XmlRootElement(name = "usersWrapper")  // ← Добавьте эту аннотацию
class UsersWrapper {
    private List<User> users;

    public List<User> getUsers() {
        return users;
    }

    public void setUsers(List<User> users) {
        this.users = users;
    }
}