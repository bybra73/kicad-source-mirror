/*
 * This program source code file is part of KiCad, a free EDA CAD application.
 *
 * Copyright (C) 2009-2018 Jean-Pierre Charras, jean-pierre.charras@ujf-grenoble.fr
 * Copyright (C) 1992-2018 KiCad Developers, see AUTHORS.txt for contributors.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, you may find one here:
 * http://www.gnu.org/licenses/old-licenses/gpl-2.0.html
 * or you may search the http://www.gnu.org website for the version 2 license,
 * or you may write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
 */

/**
 * @file class_marker_pcb.h
 * @brief Markers used to show a drc problem on boards.
 */

#ifndef CLASS_MARKER_PCB_H
#define CLASS_MARKER_PCB_H


#include <class_board_item.h>
#include <marker_base.h>
#include <drc/drc_item.h>

// Coordinates count for the basic shape marker
#define MARKER_SHAPE_POINT_COUNT 9

class MSG_PANEL_ITEM;


class MARKER_PCB : public BOARD_ITEM, public MARKER_BASE
{
public:
    MARKER_PCB( DRC_ITEM* aItem, const wxPoint& aPosition );

    ~MARKER_PCB();

    static inline bool ClassOf( const EDA_ITEM* aItem )
    {
        return aItem && PCB_MARKER_T == aItem->Type();
    }

    const KIID GetUUID() const override { return m_Uuid; }

    wxString Serialize() const;

    static MARKER_PCB* Deserialize( const wxString& data );

    void Move(const wxPoint& aMoveVector) override
    {
        m_Pos += aMoveVector;
    }

    void Rotate( const wxPoint& aRotCentre, double aAngle ) override;

    void Flip( const wxPoint& aCentre, bool aFlipLeftRight ) override;

    const wxPoint GetPosition() const override { return m_Pos; }
    void SetPosition( const wxPoint& aPos ) override { m_Pos = aPos; }

    bool HitTest( const wxPoint& aPosition, int aAccuracy = 0 ) const override
    {
        return HitTestMarker( aPosition, aAccuracy );
    }

    bool IsOnLayer( PCB_LAYER_ID aLayer ) const override;

    GAL_LAYER_ID GetColorLayer() const;

    void GetMsgPanelInfo( EDA_DRAW_FRAME* aFrame, std::vector<MSG_PANEL_ITEM>& aList ) override;

    bool Matches( wxFindReplaceData& aSearchData, void* aAuxData ) override
    {
        return BOARD_ITEM::Matches( m_rcItem->GetErrorMessage(), aSearchData );
    }

    wxString GetSelectMenuText( EDA_UNITS aUnits ) const override;

    BITMAP_DEF GetMenuImage() const override;

    const BOX2I ViewBBox() const override;

    const EDA_RECT GetBoundingBox() const override;

    void ViewGetLayers( int aLayers[], int& aCount ) const override;

#if defined(DEBUG)
    void Show( int nestLevel, std::ostream& os ) const override { ShowDummy( os ); }
#endif

    /** Get class name
     * @return  string "MARKER_PCB"
     */
    virtual wxString GetClass() const override
    {
        return wxT( "MARKER_PCB" );
    }

protected:
    KIGFX::COLOR4D getColor() const override;
};

#endif      //  CLASS_MARKER_PCB_H
