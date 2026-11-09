FIT_UINT16 Mesg::GetActiveSubFieldIndexByFieldIndex(const FIT_UINT16 fieldIndex) const
{
    if ((int) fieldIndex >= GetNumFields())
        return FIT_SUBFIELD_INDEX_MAIN_FIELD;

    const Field& field = fields[fieldIndex];
    const FIT_UINT16 numSubFields = field.GetNumSubFields();

    bool haveRefCache = false;
    FIT_UINT16 cachedRefFieldNum = 0;
    const Field* cachedRefField = FIT_NULL;
    bool cachedRefValid = false;
    FIT_SINT32 cachedRoundedRefValue = 0;

    for (FIT_UINT16 i = 0; i < numSubFields; ++i)
    {
        const Profile::SUBFIELD* subField = field.GetSubField(i);

        if (subField != FIT_NULL)
        {
            const int numMaps = (int) subField->numMaps;

            for (int j = 0; j < numMaps; ++j)
            {
                const auto& map = subField->maps[j];
                const FIT_UINT16 refFieldNum = map.refFieldNum;

                if (!haveRefCache || refFieldNum != cachedRefFieldNum)
                {
                    haveRefCache = true;
                    cachedRefFieldNum = refFieldNum;
                    cachedRefField = GetField(refFieldNum);
                    cachedRefValid = (cachedRefField != FIT_NULL);

                    if (cachedRefValid)
                    {
                        FIT_FLOAT64 refValue = cachedRefField->GetFLOAT64Value(0, FIT_SUBFIELD_INDEX_MAIN_FIELD);
                        refValue += ((refValue >= 0.0) ? (0.5) : (-0.5));
                        cachedRoundedRefValue = (FIT_SINT32)refValue;
                    }
                }

                if (cachedRefValid && cachedRoundedRefValue == map.refFieldValue)
                    return i;
            }
        }
    }

    return FIT_SUBFIELD_INDEX_MAIN_FIELD;
}
