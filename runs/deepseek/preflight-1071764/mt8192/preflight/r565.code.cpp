FIT_BOOL MesgDefinition::Supports(const MesgDefinition& mesgDef) const
{
    if (num != mesgDef.num)
        return FIT_FALSE;

    if (localNum != mesgDef.localNum)
        return FIT_FALSE;

    for (const FieldDefinition& field : mesgDef.fields)
    {
        const FIT_UINT8 fieldNum = field.GetNum();
        const FIT_UINT8 fieldSize = field.GetSize();
        bool found = false;

        for (const FieldDefinition& supportedField : fields)
        {
            if (supportedField.GetNum() == fieldNum)
            {
                if (fieldSize > supportedField.GetSize())
                    return FIT_FALSE;
                found = true;
                break;
            }
        }

        if (!found)
            return FIT_FALSE;
    }

    for (const DeveloperFieldDefinition& fieldDef : mesgDef.devFields)
    {
        const FIT_UINT8 devDataIndex = fieldDef.GetDeveloperDataIndex();
        const FIT_UINT8 fieldNum = fieldDef.GetNum();
        const FIT_UINT8 fieldSize = fieldDef.GetSize();
        bool found = false;

        for (const DeveloperFieldDefinition& supportedDef : devFields)
        {
            if (supportedDef.GetDeveloperDataIndex() == devDataIndex &&
                supportedDef.GetNum() == fieldNum)
            {
                if (fieldSize > supportedDef.GetSize())
                    return FIT_FALSE;
                found = true;
                break;
            }
        }

        if (!found)
            return FIT_FALSE;
    }

    return FIT_TRUE;
}
