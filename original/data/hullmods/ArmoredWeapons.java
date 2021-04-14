package data.hullmods;

import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;

public class ArmoredWeapons extends BaseHullMod {

	public static final float HEALTH_BONUS = 100f;
	public static final float ARMOR_BONUS = 10f;
	public static final float TURN_PENALTY = 25f;
	
	public void applyEffectsBeforeShipCreation(HullSize hullSize, MutableShipStatsAPI stats, String id) {
		stats.getArmorBonus().modifyPercent(id, ARMOR_BONUS);
		stats.getWeaponHealthBonus().modifyPercent(id, HEALTH_BONUS);
		stats.getWeaponTurnRateBonus().modifyMult(id, 1f - TURN_PENALTY * 0.01f);
	}
	
	public String getDescriptionParam(int index, HullSize hullSize) {
		if (index == 0) return "" + (int) HEALTH_BONUS + "%";
		if (index == 1) return "" + (int) TURN_PENALTY + "%";
		if (index == 2) return "" + (int) ARMOR_BONUS + "%";
		return null;
	}


}
