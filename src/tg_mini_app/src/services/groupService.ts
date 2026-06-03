import { publicApiGetUserGroups } from '@/api/sdk.gen';
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

  checkIsAdmin(groupId: number): Promise<{ message: { is_admin: boolean }, success: boolean }> {
    return apiData<{ message: { is_admin: boolean }, success: boolean }>({
      url: `/api/v1/public/groups/${groupId}/is-admin`,
      method: 'GET'
    } as any);
  }
};
