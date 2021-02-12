/*----------------------------------------------------------------------------------------------------------------
 * CupCarbon: OSM based Wireless Sensor Network design and simulation tool
 * www.cupcarbon.com
 * ----------------------------------------------------------------------------------------------------------------
 * Copyright (C) 2014 Ahcene Bounceur
 * ----------------------------------------------------------------------------------------------------------------
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *----------------------------------------------------------------------------------------------------------------*/

package overpass;

import java.util.List;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlRootElement;

/**
 * @author BOUNCEUR Ahcène
 * @version 1.0
 */
@XmlRootElement
public class Osm {
	private List<OsmWay> ways;
	private List<OsmNode> nodes;
    public Osm(){}  
    
    
    @XmlElement
    public List<OsmWay> getWay() {
        return ways;  
    }
    public void setWay(List<OsmWay> ways) {
        this.ways = ways;
    }
    
    @XmlElement
    public List<OsmNode> getNode() {
        return nodes;  
    }  
    public void setNode(List<OsmNode> nodes) {
        this.nodes = nodes;
    }
}