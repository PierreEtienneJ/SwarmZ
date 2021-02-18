import java.awt.Dimension;
import java.awt.Graphics;
import java.awt.Color;
import java.awt.BorderLayout;
import java.awt.event.ActionListener;
import java.awt.event.ItemListener;
import java.awt.event.ActionEvent;
import java.awt.event.ItemEvent;
import java.awt.event.KeyEvent;
import java.awt.event.InputEvent;
import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;
import javax.swing.JMenuBar;
import javax.swing.JMenu;
import javax.swing.JMenuItem;
import javax.swing.JCheckBoxMenuItem;
import javax.swing.JRadioButtonMenuItem;
import javax.swing.ButtonGroup;
import javax.swing.KeyStroke;


class Ardoise extends JPanel {
    Ardoise() {
		setPreferredSize(new Dimension(200, 200));
		setBackground(Color.BLUE);
		setForeground(Color.YELLOW);
    }
    
    public void paintComponent(Graphics g) {
	int largeur = getWidth();
	int hauteur = getHeight();
	
	super.paintComponent(g);
	g.fillOval(largeur/2 - 50, largeur/2 - 50, 100, 100);
    }
}

// pour le menu déroulant
class MenuCouleur extends JMenu implements ActionListener, ItemListener {
    Ardoise ardoise;
    JMenuItem itemRouge = new JMenuItem("RED");
    JMenuItem itemJaune = new JMenuItem("YELLOW");
    JMenuItem itemVert = new JMenuItem("GREEN", KeyEvent.VK_V);
    JRadioButtonMenuItem fondBleu = new JRadioButtonMenuItem("fond bleu", true);
    JRadioButtonMenuItem fondNoir = new JRadioButtonMenuItem("fond noir", false);

    MenuCouleur(final Ardoise ardoise) {
		setText("couleur");
		this.ardoise = ardoise;
		setMnemonic(KeyEvent.VK_C);

		itemRouge.setMnemonic(KeyEvent.VK_R);
		itemRouge.addActionListener(this);
		add(itemRouge);
		
		itemJaune.setAccelerator(KeyStroke.getKeyStroke
					(KeyEvent.VK_J, InputEvent.CTRL_DOWN_MASK));
		itemJaune.addActionListener(this);
		add(itemJaune);
		
		itemVert.addActionListener(this);
		add(itemVert);

		addSeparator();

		JMenu sousMenu = new JMenu("Background");
		
		ButtonGroup groupe = new ButtonGroup();

		groupe.add(fondBleu);
		fondBleu.addItemListener(this);
		sousMenu.add(fondBleu);
		
		groupe.add(fondNoir);
		fondNoir.addItemListener(this);
		sousMenu.add(fondNoir);

		add(sousMenu);
    }
    
    public void actionPerformed(ActionEvent evt) {
		Object source = evt.getSource();
		if (source == itemRouge) ardoise.setForeground(Color.RED);
		else if (source == itemJaune) ardoise.setForeground(Color.YELLOW);
		else if (source == itemVert) ardoise.setForeground(Color.GREEN);
    }
	
    public void itemStateChanged(ItemEvent evt) {
		Object source = evt.getSource();
		if (source == fondBleu) ardoise.setBackground(Color.BLUE);
		else if (source == fondNoir) ardoise.setBackground(Color.BLACK);
    }
}

class BarreMenu extends JMenuBar {
    BarreMenu(Ardoise ardoise) {
		add(new MenuCouleur(ardoise));
		}
}

class AvecMenu extends JFrame {
    AvecMenu() {
		Ardoise ardoise = new Ardoise();

		setJMenuBar(new BarreMenu(ardoise));		
		add(ardoise, BorderLayout.CENTER);
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		//setLocation(2000, 1000);
		pack();
		setVisible(true);
    }
}
public class Main extends JFrame {
	public static void main(String[] arg) {
	    new AvecMenu();
	}
}