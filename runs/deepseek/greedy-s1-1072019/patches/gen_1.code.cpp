FIT_UINT16 Mesg::GetActiveSubFieldIndexByFieldIndex(const FIT_UINT16 fieldIndex) const
{
    if ((int) fieldIndex >= GetNumFields())
        return FIT_SUBFIELD_INDEX_MAIN_FIELD;

    const Field& field = fields[fieldIndex];
    const FIT_UINT16 numSubFields = field.GetNumSubFields();

    if (numSubFields == 0)
        return FIT_SUBFIELD_INDEX_MAIN_FIELD;

    // Cache a few referenced-field values to avoid repeating GetField and
    // GetFLOAT64Value for subfields that share the same reference field.
    const Field* cachedFields[8];
    FIT_UINT16 cachedNums[8];
    FIT_SINT32 cachedVals[8];
    FIT_UINT16 cacheCount = 0;

    for (FIT_UINT16 i = 0; i < numSubFields; i++)
    {
        const Profile::SUBFIELD* subField = field.GetSubField(i);

        if (subField != FIT_NULL)
        {
            for (int j = 0; j < (int) subField->numMaps; j++)
            {
                const FIT_UINT16 refFieldNum = subField->maps[j].refFieldNum;

                const Field* refField = FIT_NULL;
                FIT_SINT32 refValueInt = 0;
                bool cached = false;

                for (FIT_UINT16 k = cacheCount; k > 0; --k)
                {
                    const FIT_UINT16 idx = (FIT_UINT16)(k - 1);
                    if (cachedNums[idx] == refFieldNum)
                    {
                        refField = cachedFields[idx];
                        refValueInt = cachedVals[idx];
                        cached = true;
                        break;
                    }
                }

                if (!cached)
                {
                    refField = GetField(refFieldNum);
                    if (refField != FIT_NULL)
                    {
                        FIT_FLOAT64 refValue = refField->GetFLOAT64Value(0, FIT_SUBFIELD_INDEX_MAIN_FIELD);
                        refValue += ((refValue >= 0.0) ? (0.5) : (-0.5));
                        refValueInt = (FIT_SINT32)refValue;
                    }

                    if (cacheCount < 8)
                    {
                        cachedNums[cacheCount] = refFieldNum;
                        cachedFields[cacheCount] = refField;
                        cachedVals[cacheCount] = refValueInt;
                        cacheCount++;
                    }
                }

                if (refField != FIT_NULL && refValueInt == subField->maps[j].refFieldValue)
                    return ((FIT_UINT16) i);
            }
        }
    }

    return FIT_SUBFIELD_INDEX_MAIN_FIELD;
}
