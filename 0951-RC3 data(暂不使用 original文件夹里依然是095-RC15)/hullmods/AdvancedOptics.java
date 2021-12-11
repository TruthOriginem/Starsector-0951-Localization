package data.hullmods;

import com.fs.starfarer.api.combat.BaseHullMod;
import com.fs.starfarer.api.combat.MutableShipStatsAPI;
import com.fs.starfarer.api.combat.ShipAPI.HullSize;

public class AdvancedOptics extends BaseHullMod {

	public static final float BEAM_RANGE_BONUS = 200f;
	//public static final float BEAM_DAMAGE_PENALTY = 25f;
	public static final float BEAM_TURN_PENALTY = 30f;
	
	public void applyEffectsBeforeShipCreation(HullSize hullSize, MutableShipStatsAPI stats, String id) {
		stats.getBeamWeaponRangeBonus().modifyFlat(id, BEAM_RANGE_BONUS);
		//stats.getBeamWeaponDamageMult().modifyPercent(id, -BEAM_DAMAGE_PENALTY);
		stats.getBeamWeaponTurnRateBonus().modifyMult(id, 1f - BEAM_TURN_PENALTY * 0.01f);
	}
	
	public String getDescriptionParam(int index, HullSize hullSize) {
		if (index == 0) return "" + (int) BEAM_RANGE_BONUS;
		//if (index == 1) return "" + (int) BEAM_DAMAGE_PENALTY;
		if (index == 1) return "" + (int) BEAM_TURN_PENALTY + "%";
		return null;
	}


}
