import { publicApiGetUserGroups, publicApiLeaveGroup } from '@/api/sdk.gen';
import type {
  PublicApiGetUserGroupsData,
  GroupsResponse,
} from '@/api/types.gen';
import { apiData } from '@/services/apiRuntime';

export const groupService = {
  getUserGroups(query?: NonNullable<PublicApiGetUserGroupsData['query']>): Promise<GroupsResponse> {
    return apiData<GroupsResponse>(
      publicApiGetUserGroups({ query })
    );
  },

  leaveGroup(groupId: Number): Promise<Record<string, unknown>> {
    return apiData<Record<string, unknown>>(
      publicApiLeaveGroup({ path: { group_id: groupId as any } })
    );
  }
};
