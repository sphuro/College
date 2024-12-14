
import java.awt.*;
import javax.swing.*;

class Gui extends JFrame {

    public Gui() {
        setSize(400, 300); // Set the window size
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setVisible(true);
    }

    // Override the paint method
    @Override
    public void paint(Graphics g) {
        super.paint(g); // Ensure the base class paints first
        g.setColor(Color.BLUE); // Set drawing color
        g.drawString("Hello, GUI!", 50, 50); // Draw a string
        g.drawRect(100, 100, 100, 50); // Draw a rectangle
        g.fillOval(200, 200, 50, 50); // Draw a filled oval
    }

    public static void main(String[] args) {
        new Gui();
    }
}

